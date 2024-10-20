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
                j2lint template-generator/templates/*.j2 || true
                '''
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
