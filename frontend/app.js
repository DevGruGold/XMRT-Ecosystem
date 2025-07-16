// XMRTNET - Starknet DeFi Platform
import { connect, disconnect } from '@starknet-io/get-starknet';
import { Provider, Contract, Account, ec, json, stark, uint256, CallData } from 'starknet';

class XMRTNetApp {
    constructor() {
        this.wallet = null;
        this.provider = null;
        this.account = null;
        this.isConnected = false;
        this.contractAddress = null;
        
        this.init();
    }

    async init() {
        console.log('Initializing XMRTNET DApp...');
        
        // Initialize Starknet provider
        this.provider = new Provider({ 
            sequencer: { 
                network: 'mainnet-alpha' 
            } 
        });
        
        this.setupEventListeners();
        this.updateUI();
        
        // Check for existing connection
        await this.checkExistingConnection();
    }

    setupEventListeners() {
        // Wallet connection
        document.getElementById('connect-wallet').addEventListener('click', () => this.connectWallet());
        document.getElementById('disconnect-wallet').addEventListener('click', () => this.disconnectWallet());
        
        // Balance and account
        document.getElementById('refresh-balance').addEventListener('click', () => this.refreshBalance());
        
        // Staking
        document.getElementById('stake-tokens').addEventListener('click', () => this.stakeTokens());
        document.getElementById('unstake-tokens').addEventListener('click', () => this.unstakeTokens());
        
        // Transactions
        document.getElementById('load-transactions').addEventListener('click', () => this.loadTransactions());
        
        // Smart contracts
        document.getElementById('deploy-contract').addEventListener('click', () => this.deployContract());
        document.getElementById('call-contract').addEventListener('click', () => this.callContract());
    }

    async checkExistingConnection() {
        try {
            // Check if wallet is already connected
            const lastConnectedWallet = localStorage.getItem('starknet-last-wallet');
            if (lastConnectedWallet) {
                await this.connectWallet();
            }
        } catch (error) {
            console.log('No existing connection found');
        }
    }

    async connectWallet() {
        try {
            this.showLoading('connect-wallet');
            
            // Use get-starknet to connect
            const wallet = await connect({
                modalMode: 'alwaysAsk',
                modalTheme: 'light'
            });

            if (wallet && wallet.isConnected) {
                this.wallet = wallet;
                this.account = wallet.account;
                this.isConnected = true;
                
                // Store connection
                localStorage.setItem('starknet-last-wallet', wallet.id);
                
                console.log('Wallet connected:', wallet);
                await this.updateWalletInfo();
                this.updateUI();
                
                this.showNotification('Wallet connected successfully!', 'success');
            }
        } catch (error) {
            console.error('Failed to connect wallet:', error);
            this.showNotification('Failed to connect wallet: ' + error.message, 'error');
        } finally {
            this.hideLoading('connect-wallet');
        }
    }

    async disconnectWallet() {
        try {
            await disconnect();
            this.wallet = null;
            this.account = null;
            this.isConnected = false;
            
            localStorage.removeItem('starknet-last-wallet');
            
            this.updateUI();
            this.showNotification('Wallet disconnected', 'info');
        } catch (error) {
            console.error('Failed to disconnect wallet:', error);
        }
    }

    async updateWalletInfo() {
        if (!this.wallet || !this.account) return;

        try {
            // Get wallet address
            const address = this.account.address;
            document.getElementById('wallet-address').textContent = this.formatAddress(address);
            
            // Get balance
            await this.refreshBalance();
            
        } catch (error) {
            console.error('Failed to update wallet info:', error);
        }
    }

    async refreshBalance() {
        if (!this.account) {
            this.showNotification('Please connect wallet first', 'warning');
            return;
        }

        try {
            this.showLoading('refresh-balance');
            
            // Get ETH balance
            const ethBalance = await this.provider.getBalance(this.account.address);
            const ethFormatted = (parseInt(ethBalance.toString()) / 1e18).toFixed(4);
            document.getElementById('balance').textContent = `${ethFormatted} ETH`;
            
            // Simulate XMRT balance (would be from contract call)
            const xmrtBalance = Math.floor(Math.random() * 1000);
            document.getElementById('xmrt-balance').textContent = `${xmrtBalance} XMRT`;
            
            this.showNotification('Balance updated', 'success');
        } catch (error) {
            console.error('Failed to refresh balance:', error);
            this.showNotification('Failed to refresh balance', 'error');
        } finally {
            this.hideLoading('refresh-balance');
        }
    }

    async stakeTokens() {
        if (!this.isConnected) {
            this.showNotification('Please connect wallet first', 'warning');
            return;
        }

        try {
            this.showLoading('stake-tokens');
            
            // Simulate staking transaction
            const amount = prompt('Enter amount to stake (XMRT):');
            if (!amount || isNaN(amount)) {
                this.showNotification('Invalid amount', 'error');
                return;
            }

            // This would be a real contract call
            await this.simulateTransaction('stake', amount);
            
            // Update staked amount display
            const currentStaked = parseInt(document.getElementById('staked-amount').textContent) || 0;
            document.getElementById('staked-amount').textContent = `${currentStaked + parseInt(amount)} XMRT`;
            
            this.showNotification(`Successfully staked ${amount} XMRT`, 'success');
        } catch (error) {
            console.error('Staking failed:', error);
            this.showNotification('Staking failed: ' + error.message, 'error');
        } finally {
            this.hideLoading('stake-tokens');
        }
    }

    async unstakeTokens() {
        if (!this.isConnected) {
            this.showNotification('Please connect wallet first', 'warning');
            return;
        }

        try {
            this.showLoading('unstake-tokens');
            
            const amount = prompt('Enter amount to unstake (XMRT):');
            if (!amount || isNaN(amount)) {
                this.showNotification('Invalid amount', 'error');
                return;
            }

            await this.simulateTransaction('unstake', amount);
            
            const currentStaked = parseInt(document.getElementById('staked-amount').textContent) || 0;
            const newStaked = Math.max(0, currentStaked - parseInt(amount));
            document.getElementById('staked-amount').textContent = `${newStaked} XMRT`;
            
            this.showNotification(`Successfully unstaked ${amount} XMRT`, 'success');
        } catch (error) {
            console.error('Unstaking failed:', error);
            this.showNotification('Unstaking failed: ' + error.message, 'error');
        } finally {
            this.hideLoading('unstake-tokens');
        }
    }

    async loadTransactions() {
        if (!this.account) {
            this.showNotification('Please connect wallet first', 'warning');
            return;
        }

        try {
            this.showLoading('load-transactions');
            
            // Simulate loading transactions
            const transactions = [
                { type: 'Stake', amount: '100 XMRT', hash: '0x123...abc', time: new Date().toLocaleString() },
                { type: 'Reward', amount: '+5 XMRT', hash: '0x456...def', time: new Date(Date.now() - 86400000).toLocaleString() },
                { type: 'Unstake', amount: '50 XMRT', hash: '0x789...ghi', time: new Date(Date.now() - 172800000).toLocaleString() }
            ];
            
            this.displayTransactions(transactions);
            this.showNotification('Transactions loaded', 'success');
        } catch (error) {
            console.error('Failed to load transactions:', error);
            this.showNotification('Failed to load transactions', 'error');
        } finally {
            this.hideLoading('load-transactions');
        }
    }

    displayTransactions(transactions) {
        const container = document.getElementById('transaction-list');
        container.innerHTML = '';
        
        transactions.forEach(tx => {
            const item = document.createElement('div');
            item.className = 'transaction-item';
            item.innerHTML = `
                <div>
                    <strong>${tx.type}</strong><br>
                    <small>${tx.time}</small>
                </div>
                <div>
                    <span>${tx.amount}</span><br>
                    <small>${tx.hash}</small>
                </div>
            `;
            container.appendChild(item);
        });
    }

    async deployContract() {
        if (!this.isConnected) {
            this.showNotification('Please connect wallet first', 'warning');
            return;
        }

        try {
            this.showLoading('deploy-contract');
            
            // Simulate contract deployment
            await this.simulateTransaction('deploy', 'XMRT Contract');
            
            this.contractAddress = '0x' + Math.random().toString(16).substr(2, 40);
            this.showNotification(`Contract deployed at: ${this.contractAddress}`, 'success');
        } catch (error) {
            console.error('Contract deployment failed:', error);
            this.showNotification('Contract deployment failed', 'error');
        } finally {
            this.hideLoading('deploy-contract');
        }
    }

    async callContract() {
        if (!this.isConnected) {
            this.showNotification('Please connect wallet first', 'warning');
            return;
        }

        if (!this.contractAddress) {
            this.showNotification('Please deploy contract first', 'warning');
            return;
        }

        try {
            this.showLoading('call-contract');
            
            // Simulate contract call
            await this.simulateTransaction('call', 'get_balance');
            
            this.showNotification('Contract call successful', 'success');
        } catch (error) {
            console.error('Contract call failed:', error);
            this.showNotification('Contract call failed', 'error');
        } finally {
            this.hideLoading('call-contract');
        }
    }

    async simulateTransaction(type, data) {
        // Simulate network delay
        await new Promise(resolve => setTimeout(resolve, 2000));
        
        // Simulate random success/failure (90% success rate)
        if (Math.random() < 0.1) {
            throw new Error('Transaction failed due to network error');
        }
        
        console.log(`Simulated ${type} transaction:`, data);
        return {
            transaction_hash: '0x' + Math.random().toString(16).substr(2, 64),
            status: 'ACCEPTED_ON_L2'
        };
    }

    updateUI() {
        const statusElement = document.getElementById('wallet-status');
        const addressElement = document.getElementById('wallet-address');
        const connectButton = document.getElementById('connect-wallet');
        const disconnectButton = document.getElementById('disconnect-wallet');

        if (this.isConnected && this.wallet) {
            statusElement.textContent = 'Connected';
            statusElement.className = 'status connected';
            addressElement.style.display = 'block';
            connectButton.style.display = 'none';
            disconnectButton.style.display = 'inline-block';
        } else {
            statusElement.textContent = 'Not Connected';
            statusElement.className = 'status disconnected';
            addressElement.style.display = 'none';
            connectButton.style.display = 'inline-block';
            disconnectButton.style.display = 'none';
        }
    }

    formatAddress(address) {
        if (!address) return '';
        return `${address.slice(0, 6)}...${address.slice(-4)}`;
    }

    showLoading(buttonId) {
        const button = document.getElementById(buttonId);
        button.disabled = true;
        button.innerHTML = '<span class="loading"></span> Loading...';
    }

    hideLoading(buttonId) {
        const button = document.getElementById(buttonId);
        button.disabled = false;
        
        // Restore original button text
        const buttonTexts = {
            'connect-wallet': 'Connect Starknet Wallet',
            'refresh-balance': 'Refresh Balance',
            'stake-tokens': 'Stake XMRT',
            'unstake-tokens': 'Unstake XMRT',
            'load-transactions': 'Load Transactions',
            'deploy-contract': 'Deploy Contract',
            'call-contract': 'Call Contract'
        };
        
        button.innerHTML = buttonTexts[buttonId] || 'Action';
    }

    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 15px 20px;
            border-radius: 5px;
            color: white;
            font-weight: 500;
            z-index: 1000;
            max-width: 300px;
            word-wrap: break-word;
        `;
        
        // Set color based on type
        const colors = {
            success: '#48bb78',
            error: '#f56565',
            warning: '#ed8936',
            info: '#4299e1'
        };
        
        notification.style.backgroundColor = colors[type] || colors.info;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        // Remove after 5 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 5000);
    }
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.xmrtApp = new XMRTNetApp();
});

// Export for potential external use
export default XMRTNetApp;

