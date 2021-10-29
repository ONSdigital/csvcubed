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

                    dir('csvcubed-devtools') {
                        sh 'poetry config virtualenvs.in-project true'
                        sh 'poetry install'
                    }

                    dir('csvcubed-models') {
                        sh 'poetry config virtualenvs.in-project true'
                        sh 'poetry install'
                    }

                    dir('csvcubed-pmd') {
                        sh 'poetry config virtualenvs.in-project true'
                        sh 'poetry install'
                        // Patch behave so that it can output the correct format for the Jenkins cucumber tool.
                        def venv_location = sh script: 'poetry env info --path', returnStdout: true
                        venv_location = venv_location.trim()
                        sh "patch -Nf -d \"${venv_location}/lib/python3.9/site-packages/behave/formatter\" -p1 < /cucumber-format.patch || true"
                    }

                    dir('csvcubed') {
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
                    dir('csvcubed-devtools') {
                        sh 'poetry run pyright . --lib'
                    }

                    dir('csvcubed-models') {
                        sh 'poetry run pyright . --lib'
                    }

                    dir('csvcubed-pmd') {
                        sh 'poetry run pyright . --lib'
                    }

                    dir('csvcubed') {
                        sh 'poetry run pyright . --lib'
                    }
            }
        }
        stage('Test') {
            steps {
                dir('csvcubed-models/tests/unit') {
                    sh "poetry run pytest --junitxml=pytest_results_models.xml"
                }
                dir('csvcubed-pmd') {
                    sh 'poetry run behave tests/behaviour --tags=-skip -f json.cucumber -o tests/behaviour/test-results.json'
                    dir('tests/unit') {
                        sh "poetry run pytest --junitxml=pytest_results_pmd.xml"
                    }
                }
                dir('csvcubed') {
                    sh 'poetry run behave tests/behaviour --tags=-skip -f json.cucumber -o tests/behaviour/test-results.json'
                    dir('tests/unit') {
                        sh "poetry run pytest --junitxml=pytest_results_csvcubed.xml"
                    }
                }

                stash name: 'test-results', includes: '**/test-results.json,**/*results*.xml' // Ensure test reports are available to be reported on.
            }
        }
        stage('Package') {
            steps {
                dir('csvcubed-devtools') {
                    sh 'poetry build'
                }

                dir('csvcubed-models') {
                    sh 'poetry build'
                }

                dir('csvcubed-pmd') {
                    sh 'poetry build'
                }

                dir('csvcubed') {
                    sh 'poetry build'
                }

                stash name: 'wheels', includes: '**/dist/*.whl'
            }
        }
        stage('Documentation') {
            steps {
                script {
                    dir('csvcubed-devtools') {
                        sh "poetry run sphinx-apidoc -F -M -a -P --tocfile index.rst -d 10 -E -o docs --implicit-namespaces -o docs csvcubeddevtools \"setup*\""
                        sh 'poetry run sphinx-build -W -b html docs docs/_build/html'
                    }

                    dir('csvcubed-models') {
                        sh "poetry run sphinx-apidoc -F -M -a -P --tocfile index.rst -d 10 -E --implicit-namespaces -o docs csvcubedmodels \"setup*\" \"csvcubedmodels/scripts\" \"/tests\""
                        sh 'poetry run sphinx-build -W -b html docs docs/_build/html'
                    }

                    dir('csvcubed-pmd') {
                        sh "poetry run sphinx-apidoc -F -M -a -P --tocfile index.rst -d 10 -E --implicit-namespaces -o docs  csvcubedpmd \"setup*\" \"tests\""
                        sh 'poetry run sphinx-build -W -b html docs docs/_build/html'
                    }

                    dir('csvcubed') {
                        sh "poetry run sphinx-apidoc -F -M -a -P --tocfile index.rst -d 10 -E --implicit-namespaces -o docs csvcubed \"setup*\" \"tests\""
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
