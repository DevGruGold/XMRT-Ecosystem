import React from 'react';

export default function MobileWallet() {
  return (
    <div>
      <h1>ðŸ“± Mobile Wallet (CashDapp Preview)</h1>
      <p>This will connect to your XMRT + XMR wallet.</p>
      <button onClick={() => alert("Send XMRT clicked")}>Send</button>
      <button onClick={() => alert("Receive clicked")}>Receive</button>
      <button onClick={() => alert("Bridge to XMRT")}>Bridge</button>
    </div>
  );
}
