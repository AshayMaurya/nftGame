// Import required modules
let Web3 = require('web3');
const solc = require('solc');
const io = require('socket.io-client');

// Connect to the WebSocket server running on localhost:3000 (or your desired server)
const socket = io('http://localhost:3000');

let web3;

// Check if Web3 is already defined (e.g., injected by MetaMask) or use a local provider
if (typeof web3 !== 'undefined') {
    web3 = new Web3(web3.currentProvider);
} else {
    web3 = new Web3(new Web3.providers.HttpProvider("http://localhost:7545"));
}

// Get the account address of the user
let from = web3.eth.accounts[0];

// Solidity source code for the smart contract
let source = "pragma solidity ^0.4.0;contract Calc{  uint count; uint result; function add(uint a, uint b) returns(uint){    count++;  result = a + b;  return result;  }  function getCount() constant returns (uint){    return count;  } function getResult() constant returns (uint){ return result; }}";

// Compile the smart contract source code
let calcCompiled = solc.compile(source, 1);
let abiDefinition = calcCompiled.contracts[':Calc'].interface;
let deployCode = calcCompiled.contracts[':Calc'].bytecode;

// Get the account address for deployment
let deployeAddr = web3.eth.accounts[0];
let calcContract = web3.eth.contract(JSON.parse(abiDefinition));

// Estimate gas required for contract deployment
let gasEstimate = web3.eth.estimateGas({ data: deployCode });
console.log(gasEstimate);

// Emit 'web3Data' event to the WebSocket server with relevant information
socket.emit('web3Data', {
    abi: JSON.parse(abiDefinition),
    bytecode: deployCode,
    gasEstimate: gasEstimate
});

// Deploy the contract and handle the callback
let myContractReturned = calcContract.new({
    data: deployCode,
    from: deployeAddr,
    gas: gasEstimate
}, function(err, myContract) {
    console.log("+++++");
    if (!err) {
        if (!myContract.address) {
            // If contract deployment is in progress, emit 'contractHash' event
            console.log("Contract deploy transaction hash: " + myContract.transactionHash);
            socket.emit('contractHash', { transactionHash: myContract.transactionHash });
        } else {
            // If contract deployment is successful, emit 'contractAddress' event
            console.log("Contract deploy address: " + myContract.address);
            socket.emit('contractAddress', { contractAddress: myContract.address });

            // Send a transaction to the deployed contract function 'add'
            myContract.add.sendTransaction(1, 2, {
                from: deployeAddr
            });

            // Call the 'getCount' and 'getResult' functions of the deployed contract
            console.log("After contract deploy, call getCount: " + myContract.getCount.call());
            console.log("Result: " + myContract.getResult.call());
        }
    } else {
        // Handle deployment error
        console.log(err);
    }
});
