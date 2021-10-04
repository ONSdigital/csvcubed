pipeline {
    agent {
        dockerfile {
            args '-u root -v /var/run/docker.sock:/var/run/docker.sock'
            reuseNode true
        }
    }
    stages {
        stage('Setup') {
            steps {
                script {
                    // Clean up any unwanted files lying about after the previous build.
                    sh "git clean -fxd --exclude='.venv'"

                    dir('devtools') {
                        sh 'poetry config virtualenvs.in-project true'
                        sh 'poetry install'
                    }

                    dir('sharedmodels') {
                        sh 'poetry config virtualenvs.in-project true'
                        sh 'poetry install'
                    }

                    dir('pmd') {
                        sh 'poetry config virtualenvs.in-project true'
                        sh 'poetry install'
                        // Patch behave so that it can output the correct format for the Jenkins cucumber tool.
                        def venv_location = sh script: 'poetry env info --path', returnStdout: true
                        venv_location = venv_location.trim()
                        sh "patch -Nf -d \"${venv_location}/lib/python3.9/site-packages/behave/formatter\" -p1 < /cucumber-format.patch || true"
                    }

                    dir('csvqb') {
                        sh 'poetry config virtualenvs.in-project true'
                        sh 'poetry install'
                        // Patch behave so that it can output the correct format for the Jenkins cucumber tool.
                        def venv_location = sh script: 'poetry env info --path', returnStdout: true
                        venv_location = venv_location.trim()
                        sh "patch -Nf -d \"${venv_location}/lib/python3.9/site-packages/behave/formatter\" -p1 < /cucumber-format.patch || true"
                    }
                }
            }
        }
        stage('Pyright') {
            agent {
                dockerfile {
                    args '-u root -v /var/run/docker.sock:/var/run/docker.sock'
                    reuseNode true
                }
            }
            steps {
                    dir('devtools') {
                        sh 'poetry run pyright . --lib'
                    }

                    dir('sharedmodels') {
                        sh 'poetry run pyright . --lib'
                    }

                    dir('pmd') {
                        sh 'poetry run pyright . --lib'
                    }

                    dir('csvqb') {
                        sh 'poetry run pyright . --lib'
                    }
            }
        }
        stage('Test') {
            steps {
                dir('sharedmodels') {
                    dir('sharedmodels/tests/unit') {
                        sh "poetry run pytest --junitxml=pytest_results_sharedmodels.xml"
                    }
                }
                dir('pmd') {
                    sh 'poetry run behave pmd/tests/behaviour --tags=-skip -f json.cucumber -o pmd/tests/behaviour/test-results.json'
                    dir('pmd/tests/unit') {
                        sh "poetry run pytest --junitxml=pytest_results_pmd.xml"
                    }
                }
                dir('csvqb') {
                    sh 'poetry run behave csvqb/tests/behaviour --tags=-skip -f json.cucumber -o csvqb/tests/behaviour/test-results.json'
                    dir('csvqb/tests/unit') {
                        sh "poetry run pytest --junitxml=pytest_results_csvqb.xml"
                    }
                }

                stash name: 'test-results', includes: '**/test-results.json,**/*results*.xml' // Ensure test reports are available to be reported on.
            }
        }
        stage('Package') {
            steps {
                dir('devtools') {
                    sh 'poetry build'
                }

                dir('sharedmodels') {
                    sh 'poetry build'
                }

                dir('pmd') {
                    sh 'poetry build'
                }

                dir('csvqb') {
                    sh 'poetry build'
                }

                stash name: 'wheels', includes: '**/dist/*.whl'
            }
        }
        stage('Documentation') {
            steps {
                script {
                    dir('devtools') {
                        sh "poetry run sphinx-apidoc -F -M -a -P --tocfile index.rst -d 10 -E -o docs --implicit-namespaces -o docs devtools \"setup*\""
                        sh 'poetry run sphinx-build -W -b html docs docs/_build/html'
                    }

                    dir('sharedmodels') {
                        sh "poetry run sphinx-apidoc -F -M -a -P --tocfile index.rst -d 10 -E --implicit-namespaces -o docs sharedmodels \"setup*\" \"sharedmodels/scripts\" \"sharedmodels/tests\""
                        sh 'poetry run sphinx-build -W -b html docs docs/_build/html'
                    }

                    dir('pmd') {
                        sh "poetry run sphinx-apidoc -F -M -a -P --tocfile index.rst -d 10 -E --implicit-namespaces -o docs  pmd \"setup*\" \"pmd/tests\""
                        sh 'poetry run sphinx-build -W -b html docs docs/_build/html'
                    }

                    dir('csvqb') {
                        sh "poetry run sphinx-apidoc -F -M -a -P --tocfile index.rst -d 10 -E --implicit-namespaces -o docs csvqb \"setup*\" \"csvqb/tests\""
                        sh 'poetry run sphinx-build -W -b html docs docs/_build/html'
                    }

                    stash name: 'docs', includes: '**/docs/_build/html/**/*'
                }
            }
        }
    }
    post {
        always {
            script {
                try {
                    unstash name: 'test-results'
                } catch (Exception e) {
                    echo 'test-results stash does not exist'
                }

                cucumber fileIncludePattern: '**/test-results.json'
                junit allowEmptyResults: true, testResults: '**/*results*.xml'

                try {
                    unstash name: 'wheels'
                } catch (Exception e) {
                    echo 'wheels stash does not exist'
                }

                try {
                    unstash name: 'docs'
                } catch (Exception e) {
                    echo 'docs stash does not exist'
                }

                archiveArtifacts artifacts: '**/dist/*.whl, **/docs/_build/html/**/*', fingerprint: true

                // Set more permissive permissions on all files so future processes/Jenkins can easily delete them.
                sh 'chmod -R ugo+rw .'
                // Clean up any unwanted files lying about.
                sh "git clean -fxd --exclude='.venv'"
            }
        }
    }
}
