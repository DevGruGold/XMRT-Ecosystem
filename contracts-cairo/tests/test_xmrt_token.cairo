use starknet::{ContractAddress, contract_address_const, testing};
use starknet::testing::{set_caller_address, set_contract_address};
use snforge_std::{declare, ContractClassTrait, DeclareResultTrait};
use xmrt_ecosystem::xmrt_token::{XMRTToken, IXMRTTokenDispatcher, IXMRTTokenDispatcherTrait};
use openzeppelin::token::erc20::interface::{IERC20Dispatcher, IERC20DispatcherTrait};

const NAME: ByteArray = "XMRT Token";
const SYMBOL: ByteArray = "XMRT";
const INITIAL_SUPPLY: u256 = 1000000000000000000000000; // 1M tokens with 18 decimals
const MAX_SUPPLY: u256 = 10000000000000000000000000; // 10M tokens with 18 decimals

fn OWNER() -> ContractAddress {
    contract_address_const::<'OWNER'>()
}

fn RECIPIENT() -> ContractAddress {
    contract_address_const::<'RECIPIENT'>()
}

fn MINTER() -> ContractAddress {
    contract_address_const::<'MINTER'>()
}

fn BURNER() -> ContractAddress {
    contract_address_const::<'BURNER'>()
}

fn USER() -> ContractAddress {
    contract_address_const::<'USER'>()
}

fn deploy_token() -> (IXMRTTokenDispatcher, IERC20Dispatcher) {
    let contract = declare("XMRTToken").unwrap().contract_class();
    
    let mut constructor_calldata = array![];
    NAME.serialize(ref constructor_calldata);
    SYMBOL.serialize(ref constructor_calldata);
    INITIAL_SUPPLY.serialize(ref constructor_calldata);
    RECIPIENT().serialize(ref constructor_calldata);
    OWNER().serialize(ref constructor_calldata);
    MAX_SUPPLY.serialize(ref constructor_calldata);
    
    let (contract_address, _) = contract.deploy(@constructor_calldata).unwrap();
    
    let xmrt_token = IXMRTTokenDispatcher { contract_address };
    let erc20_token = IERC20Dispatcher { contract_address };
    
    (xmrt_token, erc20_token)
}

#[test]
fn test_constructor() {
    let (xmrt_token, erc20_token) = deploy_token();
    
    // Test ERC20 properties
    assert(erc20_token.name() == NAME, 'Wrong name');
    assert(erc20_token.symbol() == SYMBOL, 'Wrong symbol');
    assert(erc20_token.decimals() == 18, 'Wrong decimals');
    assert(erc20_token.total_supply() == INITIAL_SUPPLY, 'Wrong total supply');
    assert(erc20_token.balance_of(RECIPIENT()) == INITIAL_SUPPLY, 'Wrong initial balance');
    
    // Test XMRT specific properties
    assert(xmrt_token.max_supply() == MAX_SUPPLY, 'Wrong max supply');
    assert(xmrt_token.total_minted() == INITIAL_SUPPLY, 'Wrong total minted');
    assert(!xmrt_token.is_paused(), 'Should not be paused');
}

#[test]
fn test_add_minter() {
    let (xmrt_token, _) = deploy_token();
    
    set_caller_address(OWNER());
    xmrt_token.add_minter(MINTER());
    
    assert(xmrt_token.is_minter(MINTER()), 'Should be minter');
}

#[test]
#[should_panic(expected: ('Caller is not the owner',))]
fn test_add_minter_not_owner() {
    let (xmrt_token, _) = deploy_token();
    
    set_caller_address(USER());
    xmrt_token.add_minter(MINTER());
}

#[test]
fn test_remove_minter() {
    let (xmrt_token, _) = deploy_token();
    
    set_caller_address(OWNER());
    xmrt_token.add_minter(MINTER());
    assert(xmrt_token.is_minter(MINTER()), 'Should be minter');
    
    xmrt_token.remove_minter(MINTER());
    assert(!xmrt_token.is_minter(MINTER()), 'Should not be minter');
}

#[test]
fn test_mint() {
    let (xmrt_token, erc20_token) = deploy_token();
    let mint_amount = 1000000000000000000000; // 1000 tokens
    
    set_caller_address(OWNER());
    xmrt_token.add_minter(MINTER());
    
    set_caller_address(MINTER());
    xmrt_token.mint(USER(), mint_amount);
    
    assert(erc20_token.balance_of(USER()) == mint_amount, 'Wrong balance after mint');
    assert(erc20_token.total_supply() == INITIAL_SUPPLY + mint_amount, 'Wrong total supply');
    assert(xmrt_token.total_minted() == INITIAL_SUPPLY + mint_amount, 'Wrong total minted');
}

#[test]
#[should_panic(expected: ('Caller is not a minter',))]
fn test_mint_not_minter() {
    let (xmrt_token, _) = deploy_token();
    let mint_amount = 1000000000000000000000;
    
    set_caller_address(USER());
    xmrt_token.mint(USER(), mint_amount);
}

#[test]
#[should_panic(expected: ('Exceeds maximum supply',))]
fn test_mint_exceeds_max_supply() {
    let (xmrt_token, _) = deploy_token();
    let mint_amount = MAX_SUPPLY; // This would exceed max supply
    
    set_caller_address(OWNER());
    xmrt_token.add_minter(MINTER());
    
    set_caller_address(MINTER());
    xmrt_token.mint(USER(), mint_amount);
}

#[test]
fn test_add_burner() {
    let (xmrt_token, _) = deploy_token();
    
    set_caller_address(OWNER());
    xmrt_token.add_burner(BURNER());
    
    assert(xmrt_token.is_burner(BURNER()), 'Should be burner');
}

#[test]
fn test_burn() {
    let (xmrt_token, erc20_token) = deploy_token();
    let burn_amount = 1000000000000000000000; // 1000 tokens
    
    set_caller_address(OWNER());
    xmrt_token.add_burner(BURNER());
    
    // First, transfer some tokens to USER for burning
    set_caller_address(RECIPIENT());
    erc20_token.transfer(USER(), burn_amount);
    
    let initial_balance = erc20_token.balance_of(USER());
    let initial_supply = erc20_token.total_supply();
    
    set_caller_address(BURNER());
    xmrt_token.burn(USER(), burn_amount);
    
    assert(erc20_token.balance_of(USER()) == initial_balance - burn_amount, 'Wrong balance after burn');
    assert(erc20_token.total_supply() == initial_supply - burn_amount, 'Wrong total supply after burn');
}

#[test]
#[should_panic(expected: ('Caller is not a burner',))]
fn test_burn_not_burner() {
    let (xmrt_token, _) = deploy_token();
    let burn_amount = 1000000000000000000000;
    
    set_caller_address(USER());
    xmrt_token.burn(USER(), burn_amount);
}

#[test]
#[should_panic(expected: ('Insufficient balance',))]
fn test_burn_insufficient_balance() {
    let (xmrt_token, _) = deploy_token();
    let burn_amount = 1000000000000000000000000000; // More than available
    
    set_caller_address(OWNER());
    xmrt_token.add_burner(BURNER());
    
    set_caller_address(BURNER());
    xmrt_token.burn(USER(), burn_amount);
}

#[test]
fn test_pause() {
    let (xmrt_token, _) = deploy_token();
    
    set_caller_address(OWNER());
    xmrt_token.pause();
    
    assert(xmrt_token.is_paused(), 'Should be paused');
}

#[test]
fn test_unpause() {
    let (xmrt_token, _) = deploy_token();
    
    set_caller_address(OWNER());
    xmrt_token.pause();
    assert(xmrt_token.is_paused(), 'Should be paused');
    
    xmrt_token.unpause();
    assert(!xmrt_token.is_paused(), 'Should not be paused');
}

#[test]
#[should_panic(expected: ('Contract is paused',))]
fn test_mint_when_paused() {
    let (xmrt_token, _) = deploy_token();
    let mint_amount = 1000000000000000000000;
    
    set_caller_address(OWNER());
    xmrt_token.add_minter(MINTER());
    xmrt_token.pause();
    
    set_caller_address(MINTER());
    xmrt_token.mint(USER(), mint_amount);
}

#[test]
#[should_panic(expected: ('Contract is paused',))]
fn test_burn_when_paused() {
    let (xmrt_token, erc20_token) = deploy_token();
    let burn_amount = 1000000000000000000000;
    
    set_caller_address(OWNER());
    xmrt_token.add_burner(BURNER());
    
    // Transfer tokens to USER first
    set_caller_address(RECIPIENT());
    erc20_token.transfer(USER(), burn_amount);
    
    set_caller_address(OWNER());
    xmrt_token.pause();
    
    set_caller_address(BURNER());
    xmrt_token.burn(USER(), burn_amount);
}

#[test]
fn test_erc20_transfer() {
    let (_, erc20_token) = deploy_token();
    let transfer_amount = 1000000000000000000000; // 1000 tokens
    
    set_caller_address(RECIPIENT());
    erc20_token.transfer(USER(), transfer_amount);
    
    assert(erc20_token.balance_of(USER()) == transfer_amount, 'Wrong balance after transfer');
    assert(erc20_token.balance_of(RECIPIENT()) == INITIAL_SUPPLY - transfer_amount, 'Wrong sender balance');
}

#[test]
fn test_erc20_approve_and_transfer_from() {
    let (_, erc20_token) = deploy_token();
    let transfer_amount = 1000000000000000000000; // 1000 tokens
    
    // Approve USER to spend tokens
    set_caller_address(RECIPIENT());
    erc20_token.approve(USER(), transfer_amount);
    
    assert(erc20_token.allowance(RECIPIENT(), USER()) == transfer_amount, 'Wrong allowance');
    
    // Transfer from RECIPIENT to another user
    set_caller_address(USER());
    erc20_token.transfer_from(RECIPIENT(), MINTER(), transfer_amount);
    
    assert(erc20_token.balance_of(MINTER()) == transfer_amount, 'Wrong balance after transfer_from');
    assert(erc20_token.balance_of(RECIPIENT()) == INITIAL_SUPPLY - transfer_amount, 'Wrong sender balance');
    assert(erc20_token.allowance(RECIPIENT(), USER()) == 0, 'Allowance should be zero');
}

