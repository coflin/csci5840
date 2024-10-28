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
    }

        stage('Ping Test') {
            steps {
                script {
                    def deviceName = params.DEVICE_NAME
                    if (deviceName) {
                        // Run ping command, check if it succeeds
                        def result = sh(script: "ping -c 4 ${deviceName}", returnStatus: true)
                        if (result != 0) {
                            error("Ping test failed for device: ${deviceName}")
                        } else {
                            echo "Ping test successful for device: ${deviceName}"
                        }
                    } else {
                        echo "No device name provided for ping test."
                    }
                }
            }
        }
    }

    post {
        success {
            echo 'Linting successful! No Jinja2 syntax errors found.'
        }
        failure {
            echo 'Linting failed! Jinja2 syntax errors detected.'
        }
    }
}
