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
                    sh "pipenv run behave pmd/tests/behaviour -D record_mode=none --tags=-skip -o test-results.json"
                }
            }
        }
    }
    post {
        always {
            cucumber 'test-results.json'
        }
    }
}