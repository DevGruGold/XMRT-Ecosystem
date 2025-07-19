import React from 'react';

export default function Bridge() {
  return (
    <div>
      <h2>ðŸŒ‰ XMRT Bridge (Simulated)</h2>
      <p>Convert your XMR earnings to XMRT tokens.</p>
      <input placeholder="Paste Monero Tx ID" />
      <button onClick={() => alert("Bridge claim submitted!")}>Claim XMRT</button>
    </div>
  );
}
