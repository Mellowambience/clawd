/**
 * Runner script for executing all phases
 */

const { executeAllPhases } = require('./executor/execute-all-phases');

async function run() {
  console.log('🌿 Running Fae Folk Community Hub Phase Execution 🌿\n');
  
  try {
    await executeAllPhases();
  } catch (error) {
    console.error('Failed to execute phases:', error);
    process.exit(1);
  }
}

run();