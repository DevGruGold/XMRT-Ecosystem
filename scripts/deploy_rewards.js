// Deploy RewardsManager pointing to deployed XMRT token
const hre = require("hardhat");
async function main() {
  const XMRT_ADDRESS = "0x77307DFbc436224d5e6f2048d2b6bDfA66998a15";
  const R = await hre.ethers.getContractFactory("RewardsManager");
  const r = await R.deploy(XMRT_ADDRESS);
  await r.deployed();
  console.log("RewardsManager deployed at:", r.address);
}
main().catch((e) => {
  console.error(e);
  process.exit(1);
});
