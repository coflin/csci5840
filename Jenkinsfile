pipeline {
    agent any

    stages {
        stage('Checkout Code') {
            steps {
                // Pull the latest code (including Jinja2 templates) from the repository
                checkout scm
            }
        }

        stage('Install J2Lint') {
            steps {
                // Install J2Lint if it's not already installed
                sh 'pip install --user j2lint'
            }
        }

        stage('Lint Jinja2 Templates') {
            steps {
                // Run J2Lint on all Jinja2 template files in the directory
                sh '''
                export PATH=$PATH:/home/student/.local/bin && j2lint template-generator/templates/*.j2
                '''
            }
        }

        stage('Ping Test') {
            steps {
                script {
                    // Identify the latest YAML file in the generated-configs directory
                    def yamlFile = sh(script: "ls -t /home/student/git/csci5840/template-generator/generated-configs/*.yaml | head -n 1", returnStdout: true).trim()
                    
                    // Check if we found a YAML file
                    if (yamlFile) {
                        def yamlContent = readYaml file: yamlFile
                        def deviceName = yamlContent?.device?.name

                        if (deviceName) {
                            // Run ping command and check if it succeeds
                            def result = sh(script: "ping -c 4 ${deviceName}", returnStatus: true)
                            if (result != 0) {
                                error("Ping test failed for device: ${deviceName}")
                            } else {
                                echo "Ping test successful for device: ${deviceName}"
                            }
                        } else {
                            echo "Device name not found in YAML file."
                        }
                    } else {
                        error("No YAML file found in generated-configs directory.")
                    }
                }
            }
        }
    }

    post {
        success {
            echo 'Jenkins Job successful. No errors found!'
        }
        failure {
            echo 'Jenkins Job failed. Please check the errors!'
        }
    }
}
