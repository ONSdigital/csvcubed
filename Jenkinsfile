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
                    sh "pipenv run behave pmd/tests/behaviour --tags=-skip -f json -o pmd/tests/behaviour/test-results.json --junit"
                    cucumber fileIncludePattern: 'pmd/tests/behaviour/test-results.json'
                    dir("pmd/tests/unit") {
                        sh "PIPENV_PIPFILE='../../../Pipfile' pipenv run python -m xmlrunner -o reports *.py"
                        junit allowEmptyResults: false, testResults: 'reports/*.xml'
                    }
                }
            }
        }
    }
    post {
        always {
            cucumber fileIncludePattern: '**/test-results.json'
            junit allowEmptyResults: true, testResults: '**/reports/*.xml'
        }
    }
}