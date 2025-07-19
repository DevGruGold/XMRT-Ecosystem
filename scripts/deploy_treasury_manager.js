// Deploy TreasuryManager to Sepolia
const hre = require("hardhat");
async function main() {
  const T = await hre.ethers.getContractFactory("TreasuryManager");
  const t = await T.deploy();
  await t.deployed();
  console.log("TreasuryManager deployed at:", t.address);
}
main().catch((e) => {
  console.error(e);
  process.exit(1);
});
