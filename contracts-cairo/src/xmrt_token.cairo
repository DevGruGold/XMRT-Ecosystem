#[starknet::contract]
mod XMRTToken {
    use starknet::{ContractAddress, get_caller_address, get_contract_address};
    use openzeppelin::token::erc20::{ERC20Component, ERC20HooksEmptyImpl};
    use openzeppelin::access::ownable::OwnableComponent;
    use openzeppelin::upgrades::UpgradeableComponent;
    use openzeppelin::upgrades::interface::IUpgradeable;
    use core::num::traits::Zero;

    component!(path: ERC20Component, storage: erc20, event: ERC20Event);
    component!(path: OwnableComponent, storage: ownable, event: OwnableEvent);
    component!(path: UpgradeableComponent, storage: upgradeable, event: UpgradeableEvent);

    // ERC20 Mixin
    #[abi(embed_v0)]
    impl ERC20MixinImpl = ERC20Component::ERC20MixinImpl<ContractState>;
    impl ERC20InternalImpl = ERC20Component::InternalImpl<ContractState>;

    // Ownable
    #[abi(embed_v0)]
    impl OwnableMixinImpl = OwnableComponent::OwnableMixinImpl<ContractState>;
    impl OwnableInternalImpl = OwnableComponent::InternalImpl<ContractState>;

    // Upgradeable
    impl UpgradeableInternalImpl = UpgradeableComponent::InternalImpl<ContractState>;

    #[storage]
    struct Storage {
        #[substorage(v0)]
        erc20: ERC20Component::Storage,
        #[substorage(v0)]
        ownable: OwnableComponent::Storage,
        #[substorage(v0)]
        upgradeable: UpgradeableComponent::Storage,
        // Custom storage
        minters: Map<ContractAddress, bool>,
        burners: Map<ContractAddress, bool>,
        paused: bool,
        max_supply: u256,
        total_minted: u256,
    }

    #[event]
    #[derive(Drop, starknet::Event)]
    enum Event {
        #[flat]
        ERC20Event: ERC20Component::Event,
        #[flat]
        OwnableEvent: OwnableComponent::Event,
        #[flat]
        UpgradeableEvent: UpgradeableComponent::Event,
        // Custom events
        MinterAdded: MinterAdded,
        MinterRemoved: MinterRemoved,
        BurnerAdded: BurnerAdded,
        BurnerRemoved: BurnerRemoved,
        Paused: Paused,
        Unpaused: Unpaused,
        TokensMinted: TokensMinted,
        TokensBurned: TokensBurned,
    }

    #[derive(Drop, starknet::Event)]
    struct MinterAdded {
        #[key]
        minter: ContractAddress,
    }

    #[derive(Drop, starknet::Event)]
    struct MinterRemoved {
        #[key]
        minter: ContractAddress,
    }

    #[derive(Drop, starknet::Event)]
    struct BurnerAdded {
        #[key]
        burner: ContractAddress,
    }

    #[derive(Drop, starknet::Event)]
    struct BurnerRemoved {
        #[key]
        burner: ContractAddress,
    }

    #[derive(Drop, starknet::Event)]
    struct Paused {}

    #[derive(Drop, starknet::Event)]
    struct Unpaused {}

    #[derive(Drop, starknet::Event)]
    struct TokensMinted {
        #[key]
        to: ContractAddress,
        amount: u256,
    }

    #[derive(Drop, starknet::Event)]
    struct TokensBurned {
        #[key]
        from: ContractAddress,
        amount: u256,
    }

    pub mod Errors {
        pub const PAUSED: felt252 = 'Contract is paused';
        pub const NOT_MINTER: felt252 = 'Caller is not a minter';
        pub const NOT_BURNER: felt252 = 'Caller is not a burner';
        pub const EXCEEDS_MAX_SUPPLY: felt252 = 'Exceeds maximum supply';
        pub const INSUFFICIENT_BALANCE: felt252 = 'Insufficient balance';
        pub const ZERO_ADDRESS: felt252 = 'Zero address not allowed';
        pub const ZERO_AMOUNT: felt252 = 'Zero amount not allowed';
    }

    #[constructor]
    fn constructor(
        ref self: ContractState,
        name: ByteArray,
        symbol: ByteArray,
        initial_supply: u256,
        recipient: ContractAddress,
        owner: ContractAddress,
        max_supply: u256
    ) {
        self.erc20.initializer(name, symbol);
        self.ownable.initializer(owner);
        
        self.max_supply.write(max_supply);
        self.paused.write(false);
        
        if initial_supply > 0 {
            self.erc20._mint(recipient, initial_supply);
            self.total_minted.write(initial_supply);
            
            self.emit(TokensMinted { to: recipient, amount: initial_supply });
        }
    }

    #[abi(embed_v0)]
    impl UpgradeableImpl of IUpgradeable<ContractState> {
        fn upgrade(ref self: ContractState, new_class_hash: starknet::ClassHash) {
            self.ownable.assert_only_owner();
            self.upgradeable._upgrade(new_class_hash);
        }
    }

    #[abi(embed_v0)]
    impl XMRTTokenImpl of super::IXMRTToken<ContractState> {
        fn mint(ref self: ContractState, to: ContractAddress, amount: u256) {
            self._assert_not_paused();
            self._assert_is_minter(get_caller_address());
            assert(!to.is_zero(), Errors::ZERO_ADDRESS);
            assert(amount > 0, Errors::ZERO_AMOUNT);
            
            let new_total = self.total_minted.read() + amount;
            assert(new_total <= self.max_supply.read(), Errors::EXCEEDS_MAX_SUPPLY);
            
            self.erc20._mint(to, amount);
            self.total_minted.write(new_total);
            
            self.emit(TokensMinted { to, amount });
        }

        fn burn(ref self: ContractState, from: ContractAddress, amount: u256) {
            self._assert_not_paused();
            self._assert_is_burner(get_caller_address());
            assert(!from.is_zero(), Errors::ZERO_ADDRESS);
            assert(amount > 0, Errors::ZERO_AMOUNT);
            
            let balance = self.erc20.balance_of(from);
            assert(balance >= amount, Errors::INSUFFICIENT_BALANCE);
            
            self.erc20._burn(from, amount);
            
            self.emit(TokensBurned { from, amount });
        }

        fn add_minter(ref self: ContractState, minter: ContractAddress) {
            self.ownable.assert_only_owner();
            assert(!minter.is_zero(), Errors::ZERO_ADDRESS);
            
            self.minters.write(minter, true);
            self.emit(MinterAdded { minter });
        }

        fn remove_minter(ref self: ContractState, minter: ContractAddress) {
            self.ownable.assert_only_owner();
            
            self.minters.write(minter, false);
            self.emit(MinterRemoved { minter });
        }

        fn add_burner(ref self: ContractState, burner: ContractAddress) {
            self.ownable.assert_only_owner();
            assert(!burner.is_zero(), Errors::ZERO_ADDRESS);
            
            self.burners.write(burner, true);
            self.emit(BurnerAdded { burner });
        }

        fn remove_burner(ref self: ContractState, burner: ContractAddress) {
            self.ownable.assert_only_owner();
            
            self.burners.write(burner, false);
            self.emit(BurnerRemoved { burner });
        }

        fn pause(ref self: ContractState) {
            self.ownable.assert_only_owner();
            self.paused.write(true);
            self.emit(Paused {});
        }

        fn unpause(ref self: ContractState) {
            self.ownable.assert_only_owner();
            self.paused.write(false);
            self.emit(Unpaused {});
        }

        fn is_minter(self: @ContractState, account: ContractAddress) -> bool {
            self.minters.read(account)
        }

        fn is_burner(self: @ContractState, account: ContractAddress) -> bool {
            self.burners.read(account)
        }

        fn is_paused(self: @ContractState) -> bool {
            self.paused.read()
        }

        fn max_supply(self: @ContractState) -> u256 {
            self.max_supply.read()
        }

        fn total_minted(self: @ContractState) -> u256 {
            self.total_minted.read()
        }
    }

    #[generate_trait]
    impl InternalImpl of InternalTrait {
        fn _assert_not_paused(self: @ContractState) {
            assert(!self.paused.read(), Errors::PAUSED);
        }

        fn _assert_is_minter(self: @ContractState, account: ContractAddress) {
            assert(self.minters.read(account), Errors::NOT_MINTER);
        }

        fn _assert_is_burner(self: @ContractState, account: ContractAddress) {
            assert(self.burners.read(account), Errors::NOT_BURNER);
        }
    }
}

#[starknet::interface]
trait IXMRTToken<TContractState> {
    fn mint(ref self: TContractState, to: ContractAddress, amount: u256);
    fn burn(ref self: TContractState, from: ContractAddress, amount: u256);
    fn add_minter(ref self: TContractState, minter: ContractAddress);
    fn remove_minter(ref self: TContractState, minter: ContractAddress);
    fn add_burner(ref self: TContractState, burner: ContractAddress);
    fn remove_burner(ref self: TContractState, burner: ContractAddress);
    fn pause(ref self: TContractState);
    fn unpause(ref self: TContractState);
    fn is_minter(self: @TContractState, account: ContractAddress) -> bool;
    fn is_burner(self: @TContractState, account: ContractAddress) -> bool;
    fn is_paused(self: @TContractState) -> bool;
    fn max_supply(self: @TContractState) -> u256;
    fn total_minted(self: @TContractState) -> u256;
}

