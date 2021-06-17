pipeline {
    agent any
    stages {
        stage('Test') {
            agent {
                dockerfile {
                    args '-u root:root -v /var/run/docker.sock:/var/run/docker.sock'
                }
            }
            steps {
                dir("pmd") {
                    sh "pipenv sync --dev"
                    dir("pmd/tests/behaviour") {
                        sh "pipenv run behave --tags=-skip -f json -o test-results.json --junit"
                    }
                }
            }
        }
    }
    post {
        always {
            cucumber 'pmd/pmd/tests/behaviour/test-results.json'
            junit allowEmptyResults: true, testResults: 'pmd/pmd/tests/behaviour/reports/*.xml'
        }
    }
}