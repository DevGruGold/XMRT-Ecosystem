/// @title XMRT
/// @notice This contract is a placeholder for the XMRT token in Cairo.
/// @dev This is a simplified version and does not include all functionalities of the Solidity counterpart.

#[contract]
mod XMRT {
    use starknet::get_caller_address;
    use starknet::ContractAddress;
    use super::IERC20::IERC20DispatcherTrait;
    use super::IERC20::IERC20Dispatcher;

    struct Storage {
        name: felt252,
        symbol: felt252,
        decimals: u8,
        total_supply: u256,
        balances: LegacyMap<ContractAddress, u256>,
        allowances: LegacyMap<(ContractAddress, ContractAddress), u256>,
    }

    #[constructor]
    fn constructor(initial_supply: u256) {
        let (name, symbol) = ('XMR Token', 'XMRT');
        let decimals = 18;
        let caller = get_caller_address();

        Internal::set_name(name);
        Internal::set_symbol(symbol);
        Internal::set_decimals(decimals);
        Internal::mint(caller, initial_supply);
    }

    #[view]
    fn name() -> felt252 {
        Internal::name()
    }

    #[view]
    fn symbol() -> felt252 {
        Internal::symbol()
    }

    #[view]
    fn decimals() -> u8 {
        Internal::decimals()
    }

    #[view]
    fn total_supply() -> u256 {
        Internal::total_supply()
    }

    #[view]
    fn balance_of(account: ContractAddress) -> u256 {
        Internal::balance_of(account)
    }

    #[view]
    fn allowance(owner: ContractAddress, spender: ContractAddress) -> u256 {
        Internal::allowance(owner, spender)
    }

    #[flat]
    fn transfer(recipient: ContractAddress, amount: u256) -> bool {
        Internal::transfer(get_caller_address(), recipient, amount)
    }

    #[flat]
    fn approve(spender: ContractAddress, amount: u256) -> bool {
        Internal::approve(get_caller_address(), spender, amount)
    }

    #[flat]
    fn transfer_from(sender: ContractAddress, recipient: ContractAddress, amount: u256) -> bool {
        Internal::transfer_from(sender, recipient, amount)
    }

    mod Internal {
        use starknet::get_caller_address;
        use starknet::ContractAddress;
        use super::Storage;

        fn name() -> felt252 {
            Storage::read(name)
        }

        fn symbol() -> felt252 {
            Storage::read(symbol)
        }

        fn decimals() -> u8 {
            Storage::read(decimals)
        }

        fn total_supply() -> u256 {
            Storage::read(total_supply)
        }

        fn balance_of(account: ContractAddress) -> u256 {
            Storage::read(balances.read(account))
        }

        fn allowance(owner: ContractAddress, spender: ContractAddress) -> u256 {
            Storage::read(allowances.read((owner, spender)))
        }

        fn set_name(name: felt252) {
            Storage::write(name, name);
        }

        fn set_symbol(symbol: felt252) {
            Storage::write(symbol, symbol);
        }

        fn set_decimals(decimals: u8) {
            Storage::write(decimals, decimals);
        }

        fn mint(recipient: ContractAddress, amount: u256) {
            let current_supply = Storage::read(total_supply);
            Storage::write(total_supply, current_supply + amount);
            let current_balance = Storage::read(balances.read(recipient));
            Storage::write(balances.write(recipient, current_balance + amount));
        }

        fn transfer(sender: ContractAddress, recipient: ContractAddress, amount: u256) -> bool {
            let sender_balance = Storage::read(balances.read(sender));
            assert(sender_balance >= amount, 'ERC20: transfer amount exceeds balance');
            Storage::write(balances.write(sender, sender_balance - amount));
            let recipient_balance = Storage::read(balances.read(recipient));
            Storage::write(balances.write(recipient, recipient_balance + amount));
            true
        }

        fn approve(spender: ContractAddress, amount: u256) -> bool {
            let owner = get_caller_address();
            Storage::write(allowances.write((owner, spender), amount));
            true
        }

        fn transfer_from(sender: ContractAddress, recipient: ContractAddress, amount: u256) -> bool {
            let caller = get_caller_address();
            let current_allowance = Storage::read(allowances.read((sender, caller)));
            assert(current_allowance >= amount, 'ERC20: transfer amount exceeds allowance');
            Storage::write(allowances.write((sender, caller), current_allowance - amount));
            Internal::transfer(sender, recipient, amount)
        }
    }

    #[interface]
    trait IERC20<T> {
        fn name(self: @T) -> felt252;
        fn symbol(self: @T) -> felt252;
        fn decimals(self: @T) -> u8;
        fn total_supply(self: @T) -> u256;
        fn balance_of(self: @T, account: ContractAddress) -> u256;
        fn allowance(self: @T, owner: ContractAddress, spender: ContractAddress) -> u256;
        fn transfer(self: @T, recipient: ContractAddress, amount: u256) -> bool;
        fn approve(self: @T, spender: ContractAddress, amount: u256) -> bool;
        fn transfer_from(self: @T, sender: ContractAddress, recipient: ContractAddress, amount: u256) -> bool;
    }
}


