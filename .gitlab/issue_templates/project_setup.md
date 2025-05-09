### Configuration

* [ ] Make sure all team members have access to the project with the correct roles.
  * [ ] Make sure that all team members have correctly configured their email notification settings.
  * [ ] Make sure to include the [:robot: Butler :robot:](https://lab.u-hopper.com/gitlab-bot) as Maintainer.
* [ ] Setup _Visibility, project features, permissions_ in the _Settings / General_ section. Disable all non-required features.
  * [ ] Should forks be allowed?
  * [ ] Is LFS needed?
  * [ ] Is the package registry required?
  * [ ] Is the Wiki required?
  * [ ] Are the Pages required?
  * [ ] Are Operations required?
  * [ ] Should Snippet be supported?
* [ ] Create and configure protected branches
  * [ ] The branch `main` should be the default one and also protected. Commits and merge operations should be allowed only to Maintainer user.
  * [ ] The branch `develop` should be protected. Commits should be allowed only to Maintainer users while merge should be allowed to both Maintainer and Developer users.
* [ ] Decide a policy for the tag (release) creation. By default, only Maintainer users should be able to configure tags.
* [ ] Setup the Merge Request configurations. The following should be true in order to merge.
  * [ ] Pipelines must succeed.
  * [ ] All threads should be resolved.
* [ ] Badges
  * [ ] Pipelines
  * [ ] Release
  * [ ] Test coverage
  * [ ] Library versions
* [ ] Setup Service Desk if required.
  * [ ] Create a _@afliant.com_ alias in order to mask the internal (and complex) email address.
  * [ ] Update the [Service Desk section in the Company Handbook](https://pages.u-hopper.com/handbook/company/procedures/service-desk).  
* [ ] Configure [Gitlab Topics](https://lab.u-hopper.com/explore/projects/topics)
  * [ ] Add the `project-template` topic if needed.
  * [ ] Does the project require being notified about an update of an internal library?


### Planning

* [ ] Define meaningful issue boards (~backlog ~planned ~"to do" ~doing ).

### Code base

* [ ] Apply the latest version of the [Project Template](https://lab.u-hopper.com/devops/ansible/project-template).
* [ ] Include a general purpose description of the project purpose in the _README.md_ file. This should be something useful for everybody in the company to understand.

### Monitoring
* [ ] Configure Sentry if required
   * [ ] Create new project in our [Sentry](https://sentry.u-hopper.com)
   * [ ] Configure the _Monitor / Error Tracking_ integration in the GitLab project.
   * [ ] Define Sentry alerts for the production environment.
