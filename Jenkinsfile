@Library('anodotLib@daria_agent') _

import com.anodot.jenkins.ci.pipeline.daria_agent.DariaAgent


node('build') {
    pipeline = new DariaAgent(this)
    pipeline.run()
}
