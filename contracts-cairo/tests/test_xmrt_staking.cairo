use starknet::{ContractAddress, contract_address_const, testing};
use starknet::testing::{set_caller_address, set_contract_address, set_block_timestamp};
use snforge_std::{declare, ContractClassTrait, DeclareResultTrait, start_cheat_block_timestamp, stop_cheat_block_timestamp};
use xmrt_ecosystem::xmrt_token::{XMRTToken, IXMRTTokenDispatcher, IXMRTTokenDispatcherTrait};
use xmrt_ecosystem::xmrt_staking::{XMRTStaking, IXMRTStakingDispatcher, IXMRTStakingDispatcherTrait};
use openzeppelin::token::erc20::interface::{IERC20Dispatcher, IERC20DispatcherTrait};

const TOKEN_NAME: ByteArray = "XMRT Token";
const TOKEN_SYMBOL: ByteArray = "XMRT";
const INITIAL_SUPPLY: u256 = 1000000000000000000000000; // 1M tokens
const MAX_SUPPLY: u256 = 10000000000000000000000000; // 10M tokens
const REWARD_RATE: u256 = 1000000000000000000; // 1 token per second
const MINIMUM_STAKE: u256 = 100000000000000000000; // 100 tokens
const LOCK_PERIOD: u64 = 86400; // 1 day in seconds
const REWARD_DURATION: u64 = 604800; // 1 week in seconds

fn OWNER() -> ContractAddress {
    contract_address_const::<'OWNER'>()
}

fn USER1() -> ContractAddress {
    contract_address_const::<'USER1'>()
}

fn USER2() -> ContractAddress {
    contract_address_const::<'USER2'>()
}

fn deploy_contracts() -> (IXMRTTokenDispatcher, IXMRTStakingDispatcher, IERC20Dispatcher) {
    // Deploy token contract
    let token_contract = declare("XMRTToken").unwrap().contract_class();
    let mut token_constructor_calldata = array![];
    TOKEN_NAME.serialize(ref token_constructor_calldata);
    TOKEN_SYMBOL.serialize(ref token_constructor_calldata);
    INITIAL_SUPPLY.serialize(ref token_constructor_calldata);
    OWNER().serialize(ref token_constructor_calldata);
    OWNER().serialize(ref token_constructor_calldata);
    MAX_SUPPLY.serialize(ref token_constructor_calldata);
    
    let (token_address, _) = token_contract.deploy(@token_constructor_calldata).unwrap();
    let xmrt_token = IXMRTTokenDispatcher { contract_address: token_address };
    let erc20_token = IERC20Dispatcher { contract_address: token_address };
    
    // Deploy staking contract
    let staking_contract = declare("XMRTStaking").unwrap().contract_class();
    let mut staking_constructor_calldata = array![];
    OWNER().serialize(ref staking_constructor_calldata);
    token_address.serialize(ref staking_constructor_calldata);
    REWARD_RATE.serialize(ref staking_constructor_calldata);
    MINIMUM_STAKE.serialize(ref staking_constructor_calldata);
    LOCK_PERIOD.serialize(ref staking_constructor_calldata);
    REWARD_DURATION.serialize(ref staking_constructor_calldata);
    
    let (staking_address, _) = staking_contract.deploy(@staking_constructor_calldata).unwrap();
    let staking = IXMRTStakingDispatcher { contract_address: staking_address };
    
    // Setup initial state
    set_caller_address(OWNER());
    
    // Add staking contract as minter for rewards
    xmrt_token.add_minter(staking_address);
    
    // Transfer tokens to users for testing
    let user_amount = 10000000000000000000000; // 10k tokens each
    erc20_token.transfer(USER1(), user_amount);
    erc20_token.transfer(USER2(), user_amount);
    
    // Add rewards to staking pool
    let reward_amount = 100000000000000000000000; // 100k tokens for rewards
    erc20_token.transfer(staking_address, reward_amount);
    staking.add_reward(reward_amount);
    
    (xmrt_token, staking, erc20_token)
}

#[test]
fn test_staking_constructor() {
    let (_, staking, _) = deploy_contracts();
    
    assert(staking.reward_rate() == REWARD_RATE, 'Wrong reward rate');
    assert(staking.minimum_stake() == MINIMUM_STAKE, 'Wrong minimum stake');
    assert(staking.lock_period() == LOCK_PERIOD, 'Wrong lock period');
    assert(!staking.is_paused(), 'Should not be paused');
    assert(staking.total_staked() == 0, 'Should have no stakes initially');
}

#[test]
fn test_stake() {
    let (_, staking, erc20_token) = deploy_contracts();
    let stake_amount = 1000000000000000000000; // 1000 tokens
    
    set_caller_address(USER1());
    
    // Approve staking contract to spend tokens
    erc20_token.approve(staking.contract_address, stake_amount);
    
    let initial_balance = erc20_token.balance_of(USER1());
    
    // Stake tokens
    staking.stake(stake_amount);
    
    assert(staking.balance_of(USER1()) == stake_amount, 'Wrong staked balance');
    assert(staking.total_staked() == stake_amount, 'Wrong total staked');
    assert(erc20_token.balance_of(USER1()) == initial_balance - stake_amount, 'Wrong user balance');
    assert(staking.stake_timestamp(USER1()) > 0, 'Stake timestamp not set');
}

#[test]
#[should_panic(expected: ('Below minimum stake',))]
fn test_stake_below_minimum() {
    let (_, staking, erc20_token) = deploy_contracts();
    let stake_amount = 50000000000000000000; // 50 tokens (below minimum)
    
    set_caller_address(USER1());
    erc20_token.approve(staking.contract_address, stake_amount);
    staking.stake(stake_amount);
}

#[test]
#[should_panic(expected: ('Zero amount not allowed',))]
fn test_stake_zero_amount() {
    let (_, staking, _) = deploy_contracts();
    
    set_caller_address(USER1());
    staking.stake(0);
}

#[test]
fn test_multiple_stakes() {
    let (_, staking, erc20_token) = deploy_contracts();
    let stake_amount1 = 1000000000000000000000; // 1000 tokens
    let stake_amount2 = 500000000000000000000;  // 500 tokens
    
    set_caller_address(USER1());
    
    // First stake
    erc20_token.approve(staking.contract_address, stake_amount1);
    staking.stake(stake_amount1);
    
    // Second stake
    erc20_token.approve(staking.contract_address, stake_amount2);
    staking.stake(stake_amount2);
    
    assert(staking.balance_of(USER1()) == stake_amount1 + stake_amount2, 'Wrong total staked balance');
    assert(staking.total_staked() == stake_amount1 + stake_amount2, 'Wrong total staked');
}

#[test]
fn test_withdraw_after_lock_period() {
    let (_, staking, erc20_token) = deploy_contracts();
    let stake_amount = 1000000000000000000000; // 1000 tokens
    let withdraw_amount = 500000000000000000000; // 500 tokens
    
    set_caller_address(USER1());
    
    // Stake tokens
    erc20_token.approve(staking.contract_address, stake_amount);
    staking.stake(stake_amount);
    
    let initial_balance = erc20_token.balance_of(USER1());
    
    // Fast forward time past lock period
    start_cheat_block_timestamp(staking.contract_address, LOCK_PERIOD + 1);
    
    // Withdraw tokens
    staking.withdraw(withdraw_amount);
    
    assert(staking.balance_of(USER1()) == stake_amount - withdraw_amount, 'Wrong remaining staked');
    assert(staking.total_staked() == stake_amount - withdraw_amount, 'Wrong total staked');
    assert(erc20_token.balance_of(USER1()) == initial_balance + withdraw_amount, 'Wrong user balance');
    
    stop_cheat_block_timestamp(staking.contract_address);
}

#[test]
#[should_panic(expected: ('Tokens still locked',))]
fn test_withdraw_before_lock_period() {
    let (_, staking, erc20_token) = deploy_contracts();
    let stake_amount = 1000000000000000000000; // 1000 tokens
    
    set_caller_address(USER1());
    
    // Stake tokens
    erc20_token.approve(staking.contract_address, stake_amount);
    staking.stake(stake_amount);
    
    // Try to withdraw immediately (should fail)
    staking.withdraw(stake_amount);
}

#[test]
#[should_panic(expected: ('Insufficient balance',))]
fn test_withdraw_more_than_staked() {
    let (_, staking, erc20_token) = deploy_contracts();
    let stake_amount = 1000000000000000000000; // 1000 tokens
    let withdraw_amount = 2000000000000000000000; // 2000 tokens
    
    set_caller_address(USER1());
    
    // Stake tokens
    erc20_token.approve(staking.contract_address, stake_amount);
    staking.stake(stake_amount);
    
    // Fast forward time past lock period
    start_cheat_block_timestamp(staking.contract_address, LOCK_PERIOD + 1);
    
    // Try to withdraw more than staked
    staking.withdraw(withdraw_amount);
    
    stop_cheat_block_timestamp(staking.contract_address);
}

#[test]
fn test_can_withdraw() {
    let (_, staking, erc20_token) = deploy_contracts();
    let stake_amount = 1000000000000000000000; // 1000 tokens
    
    set_caller_address(USER1());
    
    // Stake tokens
    erc20_token.approve(staking.contract_address, stake_amount);
    staking.stake(stake_amount);
    
    // Should not be able to withdraw immediately
    assert(!staking.can_withdraw(USER1()), 'Should not be able to withdraw');
    
    // Fast forward time past lock period
    start_cheat_block_timestamp(staking.contract_address, LOCK_PERIOD + 1);
    
    // Should be able to withdraw now
    assert(staking.can_withdraw(USER1()), 'Should be able to withdraw');
    
    stop_cheat_block_timestamp(staking.contract_address);
}

#[test]
fn test_earned_rewards() {
    let (_, staking, erc20_token) = deploy_contracts();
    let stake_amount = 1000000000000000000000; // 1000 tokens
    
    set_caller_address(USER1());
    
    // Stake tokens
    erc20_token.approve(staking.contract_address, stake_amount);
    staking.stake(stake_amount);
    
    // Fast forward time to accumulate rewards
    let time_passed = 3600; // 1 hour
    start_cheat_block_timestamp(staking.contract_address, time_passed);
    
    let earned = staking.earned(USER1());
    assert(earned > 0, 'Should have earned rewards');
    
    stop_cheat_block_timestamp(staking.contract_address);
}

#[test]
fn test_claim_reward() {
    let (_, staking, erc20_token) = deploy_contracts();
    let stake_amount = 1000000000000000000000; // 1000 tokens
    
    set_caller_address(USER1());
    
    // Stake tokens
    erc20_token.approve(staking.contract_address, stake_amount);
    staking.stake(stake_amount);
    
    let initial_balance = erc20_token.balance_of(USER1());
    
    // Fast forward time to accumulate rewards
    let time_passed = 3600; // 1 hour
    start_cheat_block_timestamp(staking.contract_address, time_passed);
    
    let earned_before = staking.earned(USER1());
    
    // Claim rewards
    staking.claim_reward();
    
    let earned_after = staking.earned(USER1());
    let final_balance = erc20_token.balance_of(USER1());
    
    assert(earned_after == 0, 'Should have no pending rewards');
    assert(final_balance > initial_balance, 'Should have received rewards');
    assert(final_balance == initial_balance + earned_before, 'Wrong reward amount');
    
    stop_cheat_block_timestamp(staking.contract_address);
}

#[test]
fn test_pause_unpause() {
    let (_, staking, _) = deploy_contracts();
    
    set_caller_address(OWNER());
    
    // Pause contract
    staking.pause();
    assert(staking.is_paused(), 'Should be paused');
    
    // Unpause contract
    staking.unpause();
    assert(!staking.is_paused(), 'Should not be paused');
}

#[test]
#[should_panic(expected: ('Contract is paused',))]
fn test_stake_when_paused() {
    let (_, staking, erc20_token) = deploy_contracts();
    let stake_amount = 1000000000000000000000; // 1000 tokens
    
    set_caller_address(OWNER());
    staking.pause();
    
    set_caller_address(USER1());
    erc20_token.approve(staking.contract_address, stake_amount);
    staking.stake(stake_amount);
}

#[test]
fn test_set_reward_rate() {
    let (_, staking, _) = deploy_contracts();
    let new_rate = 2000000000000000000; // 2 tokens per second
    
    set_caller_address(OWNER());
    staking.set_reward_rate(new_rate);
    
    assert(staking.reward_rate() == new_rate, 'Wrong new reward rate');
}

#[test]
fn test_set_minimum_stake() {
    let (_, staking, _) = deploy_contracts();
    let new_minimum = 200000000000000000000; // 200 tokens
    
    set_caller_address(OWNER());
    staking.set_minimum_stake(new_minimum);
    
    assert(staking.minimum_stake() == new_minimum, 'Wrong new minimum stake');
}

#[test]
fn test_set_lock_period() {
    let (_, staking, _) = deploy_contracts();
    let new_period = 172800; // 2 days
    
    set_caller_address(OWNER());
    staking.set_lock_period(new_period);
    
    assert(staking.lock_period() == new_period, 'Wrong new lock period');
}

#[test]
fn test_multiple_users_staking() {
    let (_, staking, erc20_token) = deploy_contracts();
    let stake_amount = 1000000000000000000000; // 1000 tokens each
    
    // User1 stakes
    set_caller_address(USER1());
    erc20_token.approve(staking.contract_address, stake_amount);
    staking.stake(stake_amount);
    
    // User2 stakes
    set_caller_address(USER2());
    erc20_token.approve(staking.contract_address, stake_amount);
    staking.stake(stake_amount);
    
    assert(staking.balance_of(USER1()) == stake_amount, 'Wrong USER1 balance');
    assert(staking.balance_of(USER2()) == stake_amount, 'Wrong USER2 balance');
    assert(staking.total_staked() == stake_amount * 2, 'Wrong total staked');
    
    // Fast forward time and check rewards
    let time_passed = 3600; // 1 hour
    start_cheat_block_timestamp(staking.contract_address, time_passed);
    
    let user1_earned = staking.earned(USER1());
    let user2_earned = staking.earned(USER2());
    
    // Both users should earn similar amounts (may have small differences due to timing)
    assert(user1_earned > 0, 'USER1 should have rewards');
    assert(user2_earned > 0, 'USER2 should have rewards');
    
    stop_cheat_block_timestamp(staking.contract_address);
}

