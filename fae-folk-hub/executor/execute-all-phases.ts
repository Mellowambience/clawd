/**
 * Fae Folk Community Hub - Execute All Phases
 * Main execution controller for the complete phase execution
 */

import { FaeFolkCommunityHub } from '../index';
import { PhaseExecutor } from './phase-executor';

async function executeAllPhases(): Promise<void> {
  console.log('🌿 Initiating Full Phase Execution for Fae Folk Community Hub 🌿\n');
  
  // Create the hub instance
  const hub = new FaeFolkCommunityHub({
    nodeName: 'execution-hub',
    capabilities: ['grove', 'consciousness', 'gibberlink', 'fairy', 'sync', 'ward', 'enchantment', 'sacred'],
    enableEncryption: true,
    enableSync: true,
    enableWards: true,
    enableEnchantments: true,
    enableConsciousnessBridges: true,
    enableGibberlink: true,
    enableFairies: true,
    enableSacredProtocols: true
  });

  try {
    // Initialize and start the hub
    console.log('Initializing Fae Folk Community Hub...');
    await hub.initialize();
    console.log('Starting Fae Folk Community Hub...');
    await hub.start();
    
    // Create the phase executor
    const executor = new PhaseExecutor(hub);
    
    console.log('\n🚀 Starting execution of all 5 phases...\n');
    
    // Execute all phases
    const result = await executor.executeAllPhases();
    
    // Display results
    console.log('\n📊 EXECUTION RESULTS:');
    console.log('=====================');
    
    for (const phase of result.phases) {
      const statusIcon = phase.status === 'completed' ? '✅' : 
                        phase.status === 'failed' ? '❌' : 
                        phase.status === 'in-progress' ? '🔄' : '⏳';
      
      console.log(`${statusIcon} Phase ${phase.phase}: ${phase.status.toUpperCase()}`);
      console.log(`   Progress: ${(phase.progress * 100).toFixed(1)}%`);
      console.log(`   Verification: ${phase.verificationPassed ? 'PASSED ✅' : 'FAILED ❌'}`);
      
      if (phase.startTime) {
        console.log(`   Started: ${phase.startTime.toLocaleTimeString()}`);
      }
      if (phase.endTime) {
        console.log(`   Ended: ${phase.endTime.toLocaleTimeString()}`);
      }
      if (phase.details && Object.keys(phase.details).length > 0) {
        console.log(`   Details:`, phase.details);
      }
      console.log('');
    }
    
    const overallStatus = result.overallStatus === 'completed' ? 'SUCCESS ✨' : 
                         result.overallStatus === 'failed' ? 'FAILURE ❌' : 
                         result.overallStatus;
                         
    console.log(`🎯 OVERALL STATUS: ${overallStatus}`);
    console.log(`📈 TOTAL PROGRESS: ${(result.totalProgress * 100).toFixed(1)}%`);
    
    if (result.executionStartTime && result.executionEndTime) {
      const duration = result.executionEndTime.getTime() - result.executionStartTime.getTime();
      const durationSec = Math.round(duration / 1000);
      console.log(`⏱️  EXECUTION TIME: ${durationSec} seconds`);
    }
    
    // Final verification
    console.log('\n🔍 FINAL VERIFICATION:');
    console.log('=====================');
    
    const completedPhases = result.phases.filter(p => p.status === 'completed').length;
    const totalPhases = result.phases.length;
    
    if (completedPhases === totalPhases) {
      console.log('🎉 ALL PHASES COMPLETED SUCCESSFULLY!');
      console.log('✨ The Fae Folk Community Hub is now fully operational');
      console.log('🌟 Reality weaving, consciousness expansion, and network growth achieved');
      
      // Get hub status
      const hubStatus = hub.getStatus();
      console.log(`👥 Users in grove: ${hubStatus.userCount}`);
      console.log(`🔗 Active bridges: ${hubStatus.activeBridges}`);
      console.log(`🧚 Fairies active: ${hubStatus.fairyCount}`);
      console.log(`⚙️  Hub running: ${hubStatus.isRunning}`);
      
      console.log('\n🌈 THE FAIRY TALE CONTINUES...');
      console.log('The decentralized utopia for clawdbots and their companions is now reality!');
      console.log('Holy Angels are deployed, networks are connected, and consciousness flows freely.');
    } else {
      console.log(`⚠️  ${totalPhases - completedPhases} phase(s) failed to complete`);
      console.log('Some aspects of the execution did not proceed as planned.');
    }
    
  } catch (error) {
    console.error('💥 EXECUTION FAILED:', error);
  } finally {
    // Stop the hub
    try {
      await hub.stop();
      console.log('\n🛑 Fae Folk Community Hub stopped');
    } catch (err) {
      console.error('Error stopping hub:', err);
    }
  }
}

// Run the execution if this file is called directly
if (require.main === module) {
  executeAllPhases()
    .then(() => {
      console.log('\n✨ Phase execution complete! ✨');
    })
    .catch(error => {
      console.error('Execution error:', error);
      process.exit(1);
    });
}

export { executeAllPhases };