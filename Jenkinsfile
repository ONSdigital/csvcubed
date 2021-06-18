pipeline {
    agent any
    stages {
        stage('Test') {
            agent {
                dockerfile {
                    args '-u root -v /var/run/docker.sock:/var/run/docker.sock'
                }
            }
            steps {
                dir("pmd") {
                    sh "pipenv sync --dev"
                    sh "pipenv run behave pmd/tests/behaviour --tags=-skip -f json -o pmd/tests/behaviour/test-results.json"
                    dir("pmd/tests/unit") {
                        sh "PIPENV_PIPFILE='../../../Pipfile' pipenv run python -m xmlrunner -o reports *.py"
                    }

                    stash name: "test-results", includes: "**/test-results.json,**/reports/*.xml"
                }
                sh "rm -rf *" // remove everything before next build (we have permissions problems since this stage is run as root)
            }
        }
    }
    post {
        always {
            steps {
                try {
                    unstash name: "test-results"
                } catch (Exception e) {
                    echo "Stash does not exist"
                }
                cucumber fileIncludePattern: '**/test-results.json'
                junit allowEmptyResults: true, testResults: '**/reports/*.xml'
            }

        }
    }
}