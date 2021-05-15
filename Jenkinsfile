/**
* Jenkins file to build and publish the test automation python muse client to the internal pypi server
* https://artifactory.sonos.com/artifactory/sonos-pypi/sonos-museclient/
* To install the latest version locally:
* pip install --extra-index-url=https://sa-plx-auto-ro:AKCp5dKswLLW5cNtcZ1mDWJEbNej4712UnAEeqPtteQxS7nJUigsZZ2qMd2kX4PYKsDM5ukdf@artifactory.sonos.com/artifactory/api/pypi/sonos-pypi/simple sonos_museclient
* This script is used by this Jenkins job:
* https://jenkins.sonos.com/main/job/pdsw-muse-api-python-client
**/

pipeline{
   agent {

        dockerfile{
            filename 'Dockerfile'
            dir '.'
            label 'Ubuntu-18.04&&!dedicated'
            registryUrl 'https://automation-docker-prod.artifactory.sonos.com/'
            registryCredentialsId '57815fa1-b8ed-4e19-8dbf-8b379f415c13'
        }
    }

    parameters{
        booleanParam(name: 'FORCED_UPLOAD', defaultValue: false, description: 'Forced execution on the repo.')
    }
    triggers{
      // Run once a day
       cron('H */1 * * *')
    }

    options {
        buildDiscarder(
            logRotator(numToKeepStr:'50', daysToKeepStr: '7', artifactDaysToKeepStr: '', artifactNumToKeepStr: '')
        )
        timeout(time: 20, unit: 'MINUTES')
        disableConcurrentBuilds()
    }

    environment{
      // Set Job environments
      FORCED_UPLOAD = "${params.FORCED_UPLOAD}"
	  PYPI_ADDR='https://artifactory.sonos.com/artifactory/api/pypi/sonos-pypi'
	  PYPI_LIST_ADDR='https://artifactory.sonos.com/artifactory/api/storage/pypi-local/sonos-museclient/'
	  GIT_API_URL='https://github.com/Sonos-Inc/pdsw-muse-api.git'
	  GIT_BRANCH='mainline'
	  GIT_SECRET='github-service-account'
	  BUILD_SRC='pdsw-muse-api'
    }

   stages{
       stage('Checkout pdsw-api repo'){
          steps{
             echo "Checking out repo ${env.BUILD_SRC} from ${env.GIT_API_URL}"
             script{
               def scm = checkout([
          $class: 'GitSCM',
          doGenerateSubmoduleConfigurations: false,
           extensions: [[$class: 'CleanBeforeCheckout'],
                      [$class: 'SubmoduleOption',
                       disableSubmodules: false,
                       parentCredentials: true,
                       recursiveSubmodules: true,
                       reference: '',
                       trackingSubmodules: false],
                      [$class: 'RelativeTargetDirectory',
                       relativeTargetDir: "${env.BUILD_SRC}/"]],
           submoduleCfg: [],
          userRemoteConfigs: [[
            url: "${env.GIT_API_URL}",
            credentialsId: "${env.GIT_SECRET}"
          ]],
          branches: [[name: "${env.GIT_BRANCH}"]]
        ])
        dir('pdsw-muse-api'){
        env.GIT_COMMIT=scm.GIT_COMMIT
        env.SHORT_GIT_SHA="${env.GIT_COMMIT}".substring(0, 7)
        env.LATEST_TAG= sh(returnStdout:  true, script: "git tag --sort=-creatordate | head -n 1").trim()
        env.BARE_LATEST_TAG ="v1.0.1-"+"${env.LATEST_TAG}".substring(1)
         }
        }
        echo "SHORT_GIT_SHA: ${env.SHORT_GIT_SHA}"
        echo "LATEST_TAG : ${env.LATEST_TAG} "
        echo "BARE_LATEST_TAG : ${env.BARE_LATEST_TAG} "
          }
       }
       stage('Fetch Artifact Status'){
          steps{
             withCredentials([[$class: 'UsernamePasswordMultiBinding',
                                  credentialsId: '57815fa1-b8ed-4e19-8dbf-8b379f415c13',
                                  usernameVariable: 'ARTIFACTORY_USER',
                                  passwordVariable: 'ARTIFACTORY_PASS'],
                                  [$class: 'StringBinding',
                                  credentialsId: 'service-github-token',
                                  variable: 'GITHUB_TOKEN']]){
               script{
                  String status = sh(script: "curl -sLI -H 'Accept:application/json' -w '\\n%{response_code}' -u '$ARTIFACTORY_USER':'$ARTIFACTORY_PASS' -X GET ${env.PYPI_LIST_ADDR}${env.BARE_LATEST_TAG}", returnStdout: true).trim()
                  env.STATUS_CODE = status.substring(status.length()-3) as int
                }
               }
          }
       }
      stage('Building and Deploy Artifact Package If Not Present'){
         steps{
            withCredentials([usernamePassword(
                                  credentialsId: '57815fa1-b8ed-4e19-8dbf-8b379f415c13',
                                  usernameVariable: 'ARTIFACTORY_USER',
                                  passwordVariable: 'ARTIFACTORY_PASSWORD')]){
             script{
                if(env.STATUS_CODE == 404 || env.FORCED_UPLOAD){
                 echo "sonos-museclient-${env.BARE_LATEST_TAG} does not exist in ${env.PYPI_ADDR}, uploading now"
                 echo "Generate the python client files"
                     sh '''#!/bin/bash
                       . /test/python/activate
                       python muse_client_generator.py  --api_source pdsw-muse-api  --api_version $BARE_LATEST_TAG || exit 1
                       sed s/replaceme/$BARE_LATEST_TAG/ setup_template.py > setup.py
                       python setup.py sdist || exit 1
                       python -m twine upload -u $ARTIFACTORY_USER -p $ARTIFACTORY_PASSWORD --verbose --repository-url $PYPI_ADDR dist/*
                       '''
                }
                else{
                  echo "sonos-museclient-${env.BARE_LATEST_TAG} already exists in ${env.PYPI_ADDR}"
                }
             }
           }
         }

      }
      stage('Test Build'){
      steps{
        echo "Testing sonos-museclient-${env.BARE_LATEST_TAG} build locally on container."
        sh '''#!/bin/bash
            . /test/python/activate
            pip install -e .
            pip list | grep muse
            pytest test/ -v --junitxml="result.xml" '''
       }
      }
   }

   post{
       always{
           echo '+++ clean up directories +++'
           junit 'result.xml'
           /*dir("${env.WORKSPACE}"){
             deleteDir()
           }*/
          }
        success{
         echo '+++ completed +++'
         setBuildStatus("Build succeeded", "SUCCESS");
        }
        failure{
          echo '!!!! failed !!!!'
          setBuildStatus("Build failed", "FAILURE")
        }
     }
}

def notifySuccess(){
  //slackSend(channel:'', message: 'Build & Upload Successful')
}

def notifyFailed(){
 //slackSend(channel:'', message:'Build & Upload Failed')
}

void setBuildStatus(String message, String state) {
  step([
      $class: "GitHubCommitStatusSetter",
      reposSource: [$class: "ManuallyEnteredRepositorySource", url: "https://github.com/Sonos-Inc/pdsw-muse-api-python-client"],
      contextSource: [$class: "ManuallyEnteredCommitContextSource", context: "ci/jenkins/build-status"],
      errorHandlers: [[$class: "ChangingBuildStatusErrorHandler", result: "UNSTABLE"]],
      statusResultSource: [ $class: "ConditionalStatusResultSource", results: [[$class: "AnyBuildResult", message: message, state: state]] ]
  ]);
}