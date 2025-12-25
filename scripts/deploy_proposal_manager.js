// Deploy ProposalManager to Sepolia
const hre = require("hardhat");
async function main() {
  const P = await hre.ethers.getContractFactory("ProposalManager");
  const p = await P.deploy();
  await p.deployed();
  console.log("ProposalManager deployed at:", p.address);
}
main().catch((e) => {
  console.error(e);
  process.exit(1);
});
