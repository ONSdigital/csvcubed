pipeline {
    agent {
        dockerfile {
            args '-u root -v /var/run/docker.sock:/var/run/docker.sock'
            reuseNode true
        }
    }
    stages {
        stage('Clean') {
            steps {
                script {
                    // Clean up any unwanted files lying about after the previous build.
                    sh "git clean -fxd --exclude='.venv'"
                }
            }
        }
        stage('Pyright') {
            when { not { buildingTag() } }
            steps {
                sh 'poetry run pyright . --lib'    
            }
        }
//         stage('Test') {
//             when { not { buildingTag() } }
//             steps {
//                 script {
//                     try {
//                         sh 'poetry run behave tests/behaviour --tags=-skip -f json.cucumber -o tests/behaviour/test-results.json'
//                         dir('tests/unit') {
//                             sh "poetry run pytest --junitxml=pytest_results_csvcubed.xml"
//                         }
//                     } catch (ex) {
//                         echo "An error occurred when testing: ${ex}"
//                         stash name: 'test-results', includes: '**/test-results.json,**/*results*.xml' // Ensure test reports are available to be reported on.
//                         throw ex
//                     }
//
//                     stash name: 'test-results', includes: '**/test-results.json,**/*results*.xml' // Ensure test reports are available to be reported on.
//                 }
//             }
//         }
        stage('Tox') {
            when { 
                buildingTag()
                tag pattern: "v\\d+\\.\\d+\\.\\d+(-RC\\d)?", comparator: "REGEXP"
            }
            agent {
                docker { image 'gsscogs/pythonversiontesting' }
            }
            steps {
                script {
                    try {
                        sh 'tox'
                    } catch (ex) {
                        echo "An error occurred testing with tox: ${ex}"
                        stash name: 'tox-test-results', includes: '**/tox-test-results-*.json,**/*results*.xml'
                        throw ex
                    }
                    // Ensure test reports are available to be reported on.
                    stash name: 'tox-test-results', includes: '**/tox-test-results-*.json,**/*results*.xml'
                }
            }
        }
        stage('Set dev version') {
            when { not { buildingTag() } }
            steps {
                // This runs when we're not building a release or release candidate
                // It sets the version of the project to something containing the decimalised version of the
                // git commit id so that the package can be automatically deployed to testpypi.

                sh 'revision="$(git rev-parse HEAD)"; decimal_rev=$(echo "obase=10; ibase=16; ${revision^^}" | bc); poetry version "0.1.0-dev$decimal_rev"'
            }
        }
        stage('Package') {
            steps {
                sh 'poetry build'

                stash name: 'wheels', includes: '**/dist/*.whl'
            }
        }
        stage('Building Documentation') {
            steps {
                script {
                    dir('external-docs'){
                        sh "python3 -m mkdocs build"
                    }

                    stash name: 'mkdocs', includes: '**/external-docs/site/**/*'
                }
            }
        }
        stage('Publishing Documentation'){
            when {
                branch 'main'
            }
            steps{
                script{
                    try {
                        withCredentials([gitUsernamePassword(credentialsId: 'csvcubed-github', gitToolName: 'git-tool')]){
                            sh 'git clone "https://github.com/GSS-Cogs/csvcubed-docs.git"'
                            dir ('csvcubed-docs') {
                                sh 'git config --global user.email "csvcubed@gsscogs.uk" && git config --global user.name "csvcubed"'
                                
                                if (fileExists("external")) {
                                    sh 'git rm -rf external'
                                }
                                sh 'mkdir external'
                                sh 'cp -r ../external-docs/site/* external'

                                if (fileExists("api-docs")) {
                                    sh 'git rm -rf api-docs'
                                }

                                sh 'touch .nojekyll'

                                sh 'git add *'
                                sh 'git add .nojekyll'
                                sh 'git commit -m "Updating documentation."'
                                // commit being built in csvcubed repo: https://github.com/GSS-Cogs/csvcubed
                                sh 'git checkout gh-pages'
                                sh 'git reset --hard main'
                                sh 'git push -f'
                            }
                        }
                    } finally {
                        sh 'rm -rf csvcubed-docs'
                    }
                }
            }
        }
        stage('Publish to Test-pypi') {
            when { not { buildingTag() } }
            steps {
                script {
                    sh "twine check dist/csvcubed*.whl"

                    try {
                        echo "Outside credentials"
                        withCredentials([usernamePassword(credentialsId: 'testpypi-robons', passwordVariable: 'TWINE_PASSWORD')]) {
                            echo "inside credentials"
                            sh 'TWINE_USERNAME="__token__" twine upload -r testpypi dist/csvcubed*.whl'
                        }
                    } catch(ex) {
                        echo "Found an exception $ex"
                    }
                }
            }
        }
//         stage('Publish to Pypi') {
//             when {
//                 buildingTag()
//                 tag pattern: "v\\d+\\.\\d+\\.\\d+(-RC\\d)?", comparator: "REGEXP"
//             }
//             environment {
//                 TWINE_USERNAME = "__token__"
//             }
//             steps {
//                 script {
//                     sh "twine check dist/csvcubed*.whl"
//
//                     withCredentials([usernamePassword(credentialsId: 'pypi-robons', passwordVariable: 'TWINE_PASSWORD')]) {
//                         sh "twine upload dist/csvcubed*.whl"
//                     }
//                 }
//             }
//         }
    }
    post {
        always {
            script {
                try {
                    unstash name: 'test-results'
                } catch (Exception e) {
                    echo 'test-results stash does not exist'
                }

                try {
                    unstash name: 'tox-test-results'
                } catch (Exception e) {
                    echo 'tox-test-results stash does not exist'
                }

                cucumber fileIncludePattern: '**/test-results.json'
                cucumber fileIncludePattern: '**/tox-test-results-*.json'
                junit allowEmptyResults: true, testResults: '**/*results*.xml'

                try {
                    unstash name: 'wheels'
                } catch (Exception e) {
                    echo 'wheels stash does not exist'
                }

                try {
                    unstash name: 'mkdocs'
                } catch (Exception e) {
                    echo 'mkdocs stash does not exist'
                }

                archiveArtifacts artifacts: '**/dist/*.whl, **/docs/_build/html/**/*, **/external-docs/site/**/*, **/test-results.json, **/tox-test-results-*.json, **/*results*.xml', fingerprint: true

                // Set more permissive permissions on all files so future processes/Jenkins can easily delete them.
                sh 'chmod -R ugo+rw .'
                // Clean up any unwanted files lying about.
                sh "git clean -fxd --exclude='.venv'"
            }
        }
    }
}
