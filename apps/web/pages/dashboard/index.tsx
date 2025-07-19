import React from 'react';

export default function Dashboard() {
  return (
    <div>
      <h1>ðŸª™ XMRT Unified Dashboard</h1>

      <section>
        <h2>Claim Mining Rewards</h2>
        <input id="uid" placeholder="Enter your Miner ID" />
        <button onClick={() => alert('Claim triggered!')}>Claim</button>
      </section>

      <section>
        <h2>Wallet</h2>
        <p>Embedded CashDapp UI coming soon...</p>
      </section>

      <section>
        <h2>Governance (Coming Soon)</h2>
        <p>Vote on proposals and shape the DAO.</p>
      </section>
    </div>
  );
}
