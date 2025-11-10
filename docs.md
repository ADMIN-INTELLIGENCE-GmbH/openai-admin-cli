Administration
Programmatically manage your organization. The Audit Logs endpoint provides a log of all actions taken in the organization for security and monitoring purposes. To access these endpoints please generate an Admin API Key through the API Platform Organization overview. Admin API keys cannot be used for non-administration endpoints. For best practices on setting up your organization, please refer to this guide

Admin API Keys
Admin API keys enable Organization Owners to programmatically manage various aspects of their organization, including users, projects, and API keys. These keys provide administrative capabilities, such as creating, updating, and deleting users; managing projects; and overseeing API key lifecycles.

Key Features of Admin API Keys:

User Management: Invite new users, update roles, and remove users from the organization.

Project Management: Create, update, archive projects, and manage user assignments within projects.

API Key Oversight: List, retrieve, and delete API keys associated with projects.

Only Organization Owners have the authority to create and utilize Admin API keys. To manage these keys, Organization Owners can navigate to the Admin Keys section of their API Platform dashboard.

For direct access to the Admin Keys management page, Organization Owners can use the following link:

https://platform.openai.com/settings/organization/admin-keys

It's crucial to handle Admin API keys with care due to their elevated permissions. Adhering to best practices, such as regular key rotation and assigning appropriate permissions, enhances security and ensures proper governance within the organization.

List all organization and project API keys.
get
 
https://api.openai.com/v1/organization/admin_api_keys
List organization API keys

Query parameters
after
string or null

Optional
limit
integer

Optional
Defaults to 20
order
string

Optional
Defaults to asc
Returns
A list of admin and project API key objects.

Example request
curl https://api.openai.com/v1/organization/admin_api_keys?after=key_abc&limit=20 \
  -H "Authorization: Bearer $OPENAI_ADMIN_KEY" \
  -H "Content-Type: application/json"
Response
{
  "object": "list",
  "data": [
    {
      "object": "organization.admin_api_key",
      "id": "key_abc",
      "name": "Main Admin Key",
      "redacted_value": "sk-admin...def",
      "created_at": 1711471533,
      "last_used_at": 1711471534,
      "owner": {
        "type": "service_account",
        "object": "organization.service_account",
        "id": "sa_456",
        "name": "My Service Account",
        "created_at": 1711471533,
        "role": "member"
      }
    }
  ],
  "first_id": "key_abc",
  "last_id": "key_abc",
  "has_more": false
}
Create admin API key
post
 
https://api.openai.com/v1/organization/admin_api_keys
Create an organization admin API key

Request body
name
string

Required
Returns
The created AdminApiKey object.

Example request
curl -X POST https://api.openai.com/v1/organization/admin_api_keys \
  -H "Authorization: Bearer $OPENAI_ADMIN_KEY" \
  -H "Content-Type: application/json" \
  -d '{
      "name": "New Admin Key"
  }'
Response
{
  "object": "organization.admin_api_key",
  "id": "key_xyz",
  "name": "New Admin Key",
  "redacted_value": "sk-admin...xyz",
  "created_at": 1711471533,
  "last_used_at": 1711471534,
  "owner": {
    "type": "user",
    "object": "organization.user",
    "id": "user_123",
    "name": "John Doe",
    "created_at": 1711471533,
    "role": "owner"
  },
  "value": "sk-admin-1234abcd"
}
Retrieve admin API key
get
 
https://api.openai.com/v1/organization/admin_api_keys/{key_id}
Retrieve a single organization API key

Path parameters
key_id
string

Required
Returns
The requested AdminApiKey object.

Example request
curl https://api.openai.com/v1/organization/admin_api_keys/key_abc \
  -H "Authorization: Bearer $OPENAI_ADMIN_KEY" \
  -H "Content-Type: application/json"
Response
{
  "object": "organization.admin_api_key",
  "id": "key_abc",
  "name": "Main Admin Key",
  "redacted_value": "sk-admin...xyz",
  "created_at": 1711471533,
  "last_used_at": 1711471534,
  "owner": {
    "type": "user",
    "object": "organization.user",
    "id": "user_123",
    "name": "John Doe",
    "created_at": 1711471533,
    "role": "owner"
  }
}
Delete admin API key
delete
 
https://api.openai.com/v1/organization/admin_api_keys/{key_id}
Delete an organization admin API key

Path parameters
key_id
string

Required
Returns
A confirmation object indicating the key was deleted.

Example request
curl -X DELETE https://api.openai.com/v1/organization/admin_api_keys/key_abc \
  -H "Authorization: Bearer $OPENAI_ADMIN_KEY" \
  -H "Content-Type: application/json"
Response
{
  "id": "key_abc",
  "object": "organization.admin_api_key.deleted",
  "deleted": true
}
The admin API key object
Represents an individual Admin API key in an org.

created_at
integer

The Unix timestamp (in seconds) of when the API key was created

id
string

The identifier, which can be referenced in API endpoints

last_used_at
integer

The Unix timestamp (in seconds) of when the API key was last used

name
string

The name of the API key

object
string

The object type, which is always organization.admin_api_key

owner
object


Show properties
redacted_value
string

The redacted value of the API key

value
string

The value of the API key. Only shown on create.

OBJECT The admin API key object
{
  "object": "organization.admin_api_key",
  "id": "key_abc",
  "name": "Main Admin Key",
  "redacted_value": "sk-admin...xyz",
  "created_at": 1711471533,
  "last_used_at": 1711471534,
  "owner": {
    "type": "user",
    "object": "organization.user",
    "id": "user_123",
    "name": "John Doe",
    "created_at": 1711471533,
    "role": "owner"
  }
}
Invites
Invite and manage invitations for an organization.

List invites
get
 
https://api.openai.com/v1/organization/invites
Returns a list of invites in the organization.

Query parameters
after
string

Optional
A cursor for use in pagination. after is an object ID that defines your place in the list. For instance, if you make a list request and receive 100 objects, ending with obj_foo, your subsequent call can include after=obj_foo in order to fetch the next page of the list.

limit
integer

Optional
Defaults to 20
A limit on the number of objects to be returned. Limit can range between 1 and 100, and the default is 20.

Returns
A list of Invite objects.

Example request
curl https://api.openai.com/v1/organization/invites?after=invite-abc&limit=20 \
  -H "Authorization: Bearer $OPENAI_ADMIN_KEY" \
  -H "Content-Type: application/json"
Response
{
  "object": "list",
  "data": [
    {
      "object": "organization.invite",
      "id": "invite-abc",
      "email": "user@example.com",
      "role": "owner",
      "status": "accepted",
      "invited_at": 1711471533,
      "expires_at": 1711471533,
      "accepted_at": 1711471533
    }
  ],
  "first_id": "invite-abc",
  "last_id": "invite-abc",
  "has_more": false
}
Create invite
post
 
https://api.openai.com/v1/organization/invites
Create an invite for a user to the organization. The invite must be accepted by the user before they have access to the organization.

Request body
email
string

Required
Send an email to this address

role
string

Required
owner or reader

projects
array

Optional
An array of projects to which membership is granted at the same time the org invite is accepted. If omitted, the user will be invited to the default project for compatibility with legacy behavior.


Show properties
Returns
The created Invite object.

Example request
curl -X POST https://api.openai.com/v1/organization/invites \
  -H "Authorization: Bearer $OPENAI_ADMIN_KEY" \
  -H "Content-Type: application/json" \
  -d '{
      "email": "anotheruser@example.com",
      "role": "reader",
      "projects": [
        {
          "id": "project-xyz",
          "role": "member"
        },
        {
          "id": "project-abc",
          "role": "owner"
        }
      ]
  }'
Response
{
  "object": "organization.invite",
  "id": "invite-def",
  "email": "anotheruser@example.com",
  "role": "reader",
  "status": "pending",
  "invited_at": 1711471533,
  "expires_at": 1711471533,
  "accepted_at": null,
  "projects": [
    {
      "id": "project-xyz",
      "role": "member"
    },
    {
      "id": "project-abc",
      "role": "owner"
    }
  ]
}
Retrieve invite
get
 
https://api.openai.com/v1/organization/invites/{invite_id}
Retrieves an invite.

Path parameters
invite_id
string

Required
The ID of the invite to retrieve.

Returns
The Invite object matching the specified ID.

Example request
curl https://api.openai.com/v1/organization/invites/invite-abc \
  -H "Authorization: Bearer $OPENAI_ADMIN_KEY" \
  -H "Content-Type: application/json"
Response
{
    "object": "organization.invite",
    "id": "invite-abc",
    "email": "user@example.com",
    "role": "owner",
    "status": "accepted",
    "invited_at": 1711471533,
    "expires_at": 1711471533,
    "accepted_at": 1711471533
}
Delete invite
delete
 
https://api.openai.com/v1/organization/invites/{invite_id}
Delete an invite. If the invite has already been accepted, it cannot be deleted.

Path parameters
invite_id
string

Required
The ID of the invite to delete.

Returns
Confirmation that the invite has been deleted

Example request
curl -X DELETE https://api.openai.com/v1/organization/invites/invite-abc \
  -H "Authorization: Bearer $OPENAI_ADMIN_KEY" \
  -H "Content-Type: application/json"
Response
{
    "object": "organization.invite.deleted",
    "id": "invite-abc",
    "deleted": true
}
The invite object
Represents an individual invite to the organization.

accepted_at
integer

The Unix timestamp (in seconds) of when the invite was accepted.

email
string

The email address of the individual to whom the invite was sent

expires_at
integer

The Unix timestamp (in seconds) of when the invite expires.

id
string

The identifier, which can be referenced in API endpoints

invited_at
integer

The Unix timestamp (in seconds) of when the invite was sent.

object
string

The object type, which is always organization.invite

projects
array

The projects that were granted membership upon acceptance of the invite.


Show properties
role
string

owner or reader

status
string

accepted,expired, or pending

OBJECT The invite object
{
  "object": "organization.invite",
  "id": "invite-abc",
  "email": "user@example.com",
  "role": "owner",
  "status": "accepted",
  "invited_at": 1711471533,
  "expires_at": 1711471533,
  "accepted_at": 1711471533,
  "projects": [
    {
      "id": "project-xyz",
      "role": "member"
    }
  ]
}
Users
Manage users and their role in an organization.

List users
get
 
https://api.openai.com/v1/organization/users
Lists all of the users in the organization.

Query parameters
after
string

Optional
A cursor for use in pagination. after is an object ID that defines your place in the list. For instance, if you make a list request and receive 100 objects, ending with obj_foo, your subsequent call can include after=obj_foo in order to fetch the next page of the list.

emails
array

Optional
Filter by the email address of users.

limit
integer

Optional
Defaults to 20
A limit on the number of objects to be returned. Limit can range between 1 and 100, and the default is 20.

Returns
A list of User objects.

Example request
curl https://api.openai.com/v1/organization/users?after=user_abc&limit=20 \
  -H "Authorization: Bearer $OPENAI_ADMIN_KEY" \
  -H "Content-Type: application/json"
Response
{
    "object": "list",
    "data": [
        {
            "object": "organization.user",
            "id": "user_abc",
            "name": "First Last",
            "email": "user@example.com",
            "role": "owner",
            "added_at": 1711471533
        }
    ],
    "first_id": "user-abc",
    "last_id": "user-xyz",
    "has_more": false
}
Modify user
post
 
https://api.openai.com/v1/organization/users/{user_id}
Modifies a user's role in the organization.

Path parameters
user_id
string

Required
The ID of the user.

Request body
role
string

Required
owner or reader

Returns
The updated User object.

Example request
curl -X POST https://api.openai.com/v1/organization/users/user_abc \
  -H "Authorization: Bearer $OPENAI_ADMIN_KEY" \
  -H "Content-Type: application/json" \
  -d '{
      "role": "owner"
  }'
Response
{
    "object": "organization.user",
    "id": "user_abc",
    "name": "First Last",
    "email": "user@example.com",
    "role": "owner",
    "added_at": 1711471533
}
Retrieve user
get
 
https://api.openai.com/v1/organization/users/{user_id}
Retrieves a user by their identifier.

Path parameters
user_id
string

Required
The ID of the user.

Returns
The User object matching the specified ID.

Example request
curl https://api.openai.com/v1/organization/users/user_abc \
  -H "Authorization: Bearer $OPENAI_ADMIN_KEY" \
  -H "Content-Type: application/json"
Response
{
    "object": "organization.user",
    "id": "user_abc",
    "name": "First Last",
    "email": "user@example.com",
    "role": "owner",
    "added_at": 1711471533
}
Delete user
delete
 
https://api.openai.com/v1/organization/users/{user_id}
Deletes a user from the organization.

Path parameters
user_id
string

Required
The ID of the user.

Returns
Confirmation of the deleted user

Example request
curl -X DELETE https://api.openai.com/v1/organization/users/user_abc \
  -H "Authorization: Bearer $OPENAI_ADMIN_KEY" \
  -H "Content-Type: application/json"
Response
{
    "object": "organization.user.deleted",
    "id": "user_abc",
    "deleted": true
}
The user object
Represents an individual user within an organization.

added_at
integer

The Unix timestamp (in seconds) of when the user was added.

email
string

The email address of the user

id
string

The identifier, which can be referenced in API endpoints

name
string

The name of the user

object
string

The object type, which is always organization.user

role
string

owner or reader

OBJECT The user object
{
    "object": "organization.user",
    "id": "user_abc",
    "name": "First Last",
    "email": "user@example.com",
    "role": "owner",
    "added_at": 1711471533
}
Projects
Manage the projects within an orgnanization includes creation, updating, and archiving or projects. The Default project cannot be archived.

List projects
get
 
https://api.openai.com/v1/organization/projects
Returns a list of projects.

Query parameters
after
string

Optional
A cursor for use in pagination. after is an object ID that defines your place in the list. For instance, if you make a list request and receive 100 objects, ending with obj_foo, your subsequent call can include after=obj_foo in order to fetch the next page of the list.

include_archived
boolean

Optional
Defaults to false
If true returns all projects including those that have been archived. Archived projects are not included by default.

limit
integer

Optional
Defaults to 20
A limit on the number of objects to be returned. Limit can range between 1 and 100, and the default is 20.

Returns
A list of Project objects.

Example request
curl https://api.openai.com/v1/organization/projects?after=proj_abc&limit=20&include_archived=false \
  -H "Authorization: Bearer $OPENAI_ADMIN_KEY" \
  -H "Content-Type: application/json"
Response
{
    "object": "list",
    "data": [
        {
            "id": "proj_abc",
            "object": "organization.project",
            "name": "Project example",
            "created_at": 1711471533,
            "archived_at": null,
            "status": "active"
        }
    ],
    "first_id": "proj-abc",
    "last_id": "proj-xyz",
    "has_more": false
}
Create project
post
 
https://api.openai.com/v1/organization/projects
Create a new project in the organization. Projects can be created and archived, but cannot be deleted.

Request body
name
string

Required
The friendly name of the project, this name appears in reports.

geography
string

Optional
Create the project with the specified data residency region. Your organization must have access to Data residency functionality in order to use. See data residency controls to review the functionality and limitations of setting this field.

Returns
The created Project object.

Example request
curl -X POST https://api.openai.com/v1/organization/projects \
  -H "Authorization: Bearer $OPENAI_ADMIN_KEY" \
  -H "Content-Type: application/json" \
  -d '{
      "name": "Project ABC"
  }'
Response
{
    "id": "proj_abc",
    "object": "organization.project",
    "name": "Project ABC",
    "created_at": 1711471533,
    "archived_at": null,
    "status": "active"
}
Retrieve project
get
 
https://api.openai.com/v1/organization/projects/{project_id}
Retrieves a project.

Path parameters
project_id
string

Required
The ID of the project.

Returns
The Project object matching the specified ID.

Example request
curl https://api.openai.com/v1/organization/projects/proj_abc \
  -H "Authorization: Bearer $OPENAI_ADMIN_KEY" \
  -H "Content-Type: application/json"
Response
{
    "id": "proj_abc",
    "object": "organization.project",
    "name": "Project example",
    "created_at": 1711471533,
    "archived_at": null,
    "status": "active"
}
Modify project
post
 
https://api.openai.com/v1/organization/projects/{project_id}
Modifies a project in the organization.

Path parameters
project_id
string

Required
The ID of the project.

Request body
name
string

Required
The updated name of the project, this name appears in reports.

Returns
The updated Project object.

Example request
curl -X POST https://api.openai.com/v1/organization/projects/proj_abc \
  -H "Authorization: Bearer $OPENAI_ADMIN_KEY" \
  -H "Content-Type: application/json" \
  -d '{
      "name": "Project DEF"
  }'
Archive project
post
 
https://api.openai.com/v1/organization/projects/{project_id}/archive
Archives a project in the organization. Archived projects cannot be used or updated.

Path parameters
project_id
string

Required
The ID of the project.

Returns
The archived Project object.

Example request
curl -X POST https://api.openai.com/v1/organization/projects/proj_abc/archive \
  -H "Authorization: Bearer $OPENAI_ADMIN_KEY" \
  -H "Content-Type: application/json"
Response
{
    "id": "proj_abc",
    "object": "organization.project",
    "name": "Project DEF",
    "created_at": 1711471533,
    "archived_at": 1711471533,
    "status": "archived"
}
The project object
Represents an individual project.

archived_at
integer

The Unix timestamp (in seconds) of when the project was archived or null.

created_at
integer

The Unix timestamp (in seconds) of when the project was created.

id
string

The identifier, which can be referenced in API endpoints

name
string

The name of the project. This appears in reporting.

object
string

The object type, which is always organization.project

status
string

active or archived

OBJECT The project object
{
    "id": "proj_abc",
    "object": "organization.project",
    "name": "Project example",
    "created_at": 1711471533,
    "archived_at": null,
    "status": "active"
}
Project users
Manage users within a project, including adding, updating roles, and removing users.

List project users
get
 
https://api.openai.com/v1/organization/projects/{project_id}/users
Returns a list of users in the project.

Path parameters
project_id
string

Required
The ID of the project.

Query parameters
after
string

Optional
A cursor for use in pagination. after is an object ID that defines your place in the list. For instance, if you make a list request and receive 100 objects, ending with obj_foo, your subsequent call can include after=obj_foo in order to fetch the next page of the list.

limit
integer

Optional
Defaults to 20
A limit on the number of objects to be returned. Limit can range between 1 and 100, and the default is 20.

Returns
A list of ProjectUser objects.

Example request
curl https://api.openai.com/v1/organization/projects/proj_abc/users?after=user_abc&limit=20 \
  -H "Authorization: Bearer $OPENAI_ADMIN_KEY" \
  -H "Content-Type: application/json"
Response
{
    "object": "list",
    "data": [
        {
            "object": "organization.project.user",
            "id": "user_abc",
            "name": "First Last",
            "email": "user@example.com",
            "role": "owner",
            "added_at": 1711471533
        }
    ],
    "first_id": "user-abc",
    "last_id": "user-xyz",
    "has_more": false
}
Create project user
post
 
https://api.openai.com/v1/organization/projects/{project_id}/users
Adds a user to the project. Users must already be members of the organization to be added to a project.

Path parameters
project_id
string

Required
The ID of the project.

Request body
role
string

Required
owner or member

user_id
string

Required
The ID of the user.

Returns
The created ProjectUser object.

Example request
curl -X POST https://api.openai.com/v1/organization/projects/proj_abc/users \
  -H "Authorization: Bearer $OPENAI_ADMIN_KEY" \
  -H "Content-Type: application/json" \
  -d '{
      "user_id": "user_abc",
      "role": "member"
  }'
Response
{
    "object": "organization.project.user",
    "id": "user_abc",
    "email": "user@example.com",
    "role": "owner",
    "added_at": 1711471533
}
Retrieve project user
get
 
https://api.openai.com/v1/organization/projects/{project_id}/users/{user_id}
Retrieves a user in the project.

Path parameters
project_id
string

Required
The ID of the project.

user_id
string

Required
The ID of the user.

Returns
The ProjectUser object matching the specified ID.

Example request
curl https://api.openai.com/v1/organization/projects/proj_abc/users/user_abc \
  -H "Authorization: Bearer $OPENAI_ADMIN_KEY" \
  -H "Content-Type: application/json"
Response
{
    "object": "organization.project.user",
    "id": "user_abc",
    "name": "First Last",
    "email": "user@example.com",
    "role": "owner",
    "added_at": 1711471533
}
Modify project user
post
 
https://api.openai.com/v1/organization/projects/{project_id}/users/{user_id}
Modifies a user's role in the project.

Path parameters
project_id
string

Required
The ID of the project.

user_id
string

Required
The ID of the user.

Request body
role
string

Required
owner or member

Returns
The updated ProjectUser object.

Example request
curl -X POST https://api.openai.com/v1/organization/projects/proj_abc/users/user_abc \
  -H "Authorization: Bearer $OPENAI_ADMIN_KEY" \
  -H "Content-Type: application/json" \
  -d '{
      "role": "owner"
  }'
Response
{
    "object": "organization.project.user",
    "id": "user_abc",
    "name": "First Last",
    "email": "user@example.com",
    "role": "owner",
    "added_at": 1711471533
}
Delete project user
delete
 
https://api.openai.com/v1/organization/projects/{project_id}/users/{user_id}
Deletes a user from the project.

Path parameters
project_id
string

Required
The ID of the project.

user_id
string

Required
The ID of the user.

Returns
Confirmation that project has been deleted or an error in case of an archived project, which has no users

Example request
curl -X DELETE https://api.openai.com/v1/organization/projects/proj_abc/users/user_abc \
  -H "Authorization: Bearer $OPENAI_ADMIN_KEY" \
  -H "Content-Type: application/json"
Response
{
    "object": "organization.project.user.deleted",
    "id": "user_abc",
    "deleted": true
}
The project user object
Represents an individual user in a project.

added_at
integer

The Unix timestamp (in seconds) of when the project was added.

email
string

The email address of the user

id
string

The identifier, which can be referenced in API endpoints

name
string

The name of the user

object
string

The object type, which is always organization.project.user

role
string

owner or member

OBJECT The project user object
{
    "object": "organization.project.user",
    "id": "user_abc",
    "name": "First Last",
    "email": "user@example.com",
    "role": "owner",
    "added_at": 1711471533
}
Project service accounts
Manage service accounts within a project. A service account is a bot user that is not associated with a user. If a user leaves an organization, their keys and membership in projects will no longer work. Service accounts do not have this limitation. However, service accounts can also be deleted from a project.

List project service accounts
get
 
https://api.openai.com/v1/organization/projects/{project_id}/service_accounts
Returns a list of service accounts in the project.

Path parameters
project_id
string

Required
The ID of the project.

Query parameters
after
string

Optional
A cursor for use in pagination. after is an object ID that defines your place in the list. For instance, if you make a list request and receive 100 objects, ending with obj_foo, your subsequent call can include after=obj_foo in order to fetch the next page of the list.

limit
integer

Optional
Defaults to 20
A limit on the number of objects to be returned. Limit can range between 1 and 100, and the default is 20.

Returns
A list of ProjectServiceAccount objects.

Example request
curl https://api.openai.com/v1/organization/projects/proj_abc/service_accounts?after=custom_id&limit=20 \
  -H "Authorization: Bearer $OPENAI_ADMIN_KEY" \
  -H "Content-Type: application/json"
Response
{
    "object": "list",
    "data": [
        {
            "object": "organization.project.service_account",
            "id": "svc_acct_abc",
            "name": "Service Account",
            "role": "owner",
            "created_at": 1711471533
        }
    ],
    "first_id": "svc_acct_abc",
    "last_id": "svc_acct_xyz",
    "has_more": false
}
Create project service account
post
 
https://api.openai.com/v1/organization/projects/{project_id}/service_accounts
Creates a new service account in the project. This also returns an unredacted API key for the service account.

Path parameters
project_id
string

Required
The ID of the project.

Request body
name
string

Required
The name of the service account being created.

Returns
The created ProjectServiceAccount object.

Example request
curl -X POST https://api.openai.com/v1/organization/projects/proj_abc/service_accounts \
  -H "Authorization: Bearer $OPENAI_ADMIN_KEY" \
  -H "Content-Type: application/json" \
  -d '{
      "name": "Production App"
  }'
Response
{
    "object": "organization.project.service_account",
    "id": "svc_acct_abc",
    "name": "Production App",
    "role": "member",
    "created_at": 1711471533,
    "api_key": {
        "object": "organization.project.service_account.api_key",
        "value": "sk-abcdefghijklmnop123",
        "name": "Secret Key",
        "created_at": 1711471533,
        "id": "key_abc"
    }
}
Retrieve project service account
get
 
https://api.openai.com/v1/organization/projects/{project_id}/service_accounts/{service_account_id}
Retrieves a service account in the project.

Path parameters
project_id
string

Required
The ID of the project.

service_account_id
string

Required
The ID of the service account.

Returns
The ProjectServiceAccount object matching the specified ID.

Example request
curl https://api.openai.com/v1/organization/projects/proj_abc/service_accounts/svc_acct_abc \
  -H "Authorization: Bearer $OPENAI_ADMIN_KEY" \
  -H "Content-Type: application/json"
Response
{
    "object": "organization.project.service_account",
    "id": "svc_acct_abc",
    "name": "Service Account",
    "role": "owner",
    "created_at": 1711471533
}
Delete project service account
delete
 
https://api.openai.com/v1/organization/projects/{project_id}/service_accounts/{service_account_id}
Deletes a service account from the project.

Path parameters
project_id
string

Required
The ID of the project.

service_account_id
string

Required
The ID of the service account.

Returns
Confirmation of service account being deleted, or an error in case of an archived project, which has no service accounts

Example request
curl -X DELETE https://api.openai.com/v1/organization/projects/proj_abc/service_accounts/svc_acct_abc \
  -H "Authorization: Bearer $OPENAI_ADMIN_KEY" \
  -H "Content-Type: application/json"
Response
{
    "object": "organization.project.service_account.deleted",
    "id": "svc_acct_abc",
    "deleted": true
}
The project service account object
Represents an individual service account in a project.

created_at
integer

The Unix timestamp (in seconds) of when the service account was created

id
string

The identifier, which can be referenced in API endpoints

name
string

The name of the service account

object
string

The object type, which is always organization.project.service_account

role
string

owner or member

OBJECT The project service account object
{
    "object": "organization.project.service_account",
    "id": "svc_acct_abc",
    "name": "Service Account",
    "role": "owner",
    "created_at": 1711471533
}
Project API keys
Manage API keys for a given project. Supports listing and deleting keys for users. This API does not allow issuing keys for users, as users need to authorize themselves to generate keys.

List project API keys
get
 
https://api.openai.com/v1/organization/projects/{project_id}/api_keys
Returns a list of API keys in the project.

Path parameters
project_id
string

Required
The ID of the project.

Query parameters
after
string

Optional
A cursor for use in pagination. after is an object ID that defines your place in the list. For instance, if you make a list request and receive 100 objects, ending with obj_foo, your subsequent call can include after=obj_foo in order to fetch the next page of the list.

limit
integer

Optional
Defaults to 20
A limit on the number of objects to be returned. Limit can range between 1 and 100, and the default is 20.

Returns
A list of ProjectApiKey objects.

Example request
curl https://api.openai.com/v1/organization/projects/proj_abc/api_keys?after=key_abc&limit=20 \
  -H "Authorization: Bearer $OPENAI_ADMIN_KEY" \
  -H "Content-Type: application/json"
Response
{
    "object": "list",
    "data": [
        {
            "object": "organization.project.api_key",
            "redacted_value": "sk-abc...def",
            "name": "My API Key",
            "created_at": 1711471533,
            "last_used_at": 1711471534,
            "id": "key_abc",
            "owner": {
                "type": "user",
                "user": {
                    "object": "organization.project.user",
                    "id": "user_abc",
                    "name": "First Last",
                    "email": "user@example.com",
                    "role": "owner",
                    "added_at": 1711471533
                }
            }
        }
    ],
    "first_id": "key_abc",
    "last_id": "key_xyz",
    "has_more": false
}
Retrieve project API key
get
 
https://api.openai.com/v1/organization/projects/{project_id}/api_keys/{key_id}
Retrieves an API key in the project.

Path parameters
key_id
string

Required
The ID of the API key.

project_id
string

Required
The ID of the project.

Returns
The ProjectApiKey object matching the specified ID.

Example request
curl https://api.openai.com/v1/organization/projects/proj_abc/api_keys/key_abc \
  -H "Authorization: Bearer $OPENAI_ADMIN_KEY" \
  -H "Content-Type: application/json"
Response
{
    "object": "organization.project.api_key",
    "redacted_value": "sk-abc...def",
    "name": "My API Key",
    "created_at": 1711471533,
    "last_used_at": 1711471534,
    "id": "key_abc",
    "owner": {
        "type": "user",
        "user": {
            "object": "organization.project.user",
            "id": "user_abc",
            "name": "First Last",
            "email": "user@example.com",
            "role": "owner",
            "added_at": 1711471533
        }
    }
}
Delete project API key
delete
 
https://api.openai.com/v1/organization/projects/{project_id}/api_keys/{key_id}
Deletes an API key from the project.

Path parameters
key_id
string

Required
The ID of the API key.

project_id
string

Required
The ID of the project.

Returns
Confirmation of the key's deletion or an error if the key belonged to a service account

Example request
curl -X DELETE https://api.openai.com/v1/organization/projects/proj_abc/api_keys/key_abc \
  -H "Authorization: Bearer $OPENAI_ADMIN_KEY" \
  -H "Content-Type: application/json"
Response
{
    "object": "organization.project.api_key.deleted",
    "id": "key_abc",
    "deleted": true
}
The project API key object
Represents an individual API key in a project.

created_at
integer

The Unix timestamp (in seconds) of when the API key was created

id
string

The identifier, which can be referenced in API endpoints

last_used_at
integer

The Unix timestamp (in seconds) of when the API key was last used.

name
string

The name of the API key

object
string

The object type, which is always organization.project.api_key

owner
object


Show properties
redacted_value
string

The redacted value of the API key

OBJECT The project API key object
{
    "object": "organization.project.api_key",
    "redacted_value": "sk-abc...def",
    "name": "My API Key",
    "created_at": 1711471533,
    "last_used_at": 1711471534,
    "id": "key_abc",
    "owner": {
        "type": "user",
        "user": {
            "object": "organization.project.user",
            "id": "user_abc",
            "name": "First Last",
            "email": "user@example.com",
            "role": "owner",
            "created_at": 1711471533
        }
    }
}
Project rate limits
Manage rate limits per model for projects. Rate limits may be configured to be equal to or lower than the organization's rate limits.

List project rate limits
get
 
https://api.openai.com/v1/organization/projects/{project_id}/rate_limits
Returns the rate limits per model for a project.

Path parameters
project_id
string

Required
The ID of the project.

Query parameters
after
string

Optional
A cursor for use in pagination. after is an object ID that defines your place in the list. For instance, if you make a list request and receive 100 objects, ending with obj_foo, your subsequent call can include after=obj_foo in order to fetch the next page of the list.

before
string

Optional
A cursor for use in pagination. before is an object ID that defines your place in the list. For instance, if you make a list request and receive 100 objects, beginning with obj_foo, your subsequent call can include before=obj_foo in order to fetch the previous page of the list.

limit
integer

Optional
Defaults to 100
A limit on the number of objects to be returned. The default is 100.

Returns
A list of ProjectRateLimit objects.

Example request
curl https://api.openai.com/v1/organization/projects/proj_abc/rate_limits?after=rl_xxx&limit=20 \
  -H "Authorization: Bearer $OPENAI_ADMIN_KEY" \
  -H "Content-Type: application/json"
Response
{
    "object": "list",
    "data": [
        {
          "object": "project.rate_limit",
          "id": "rl-ada",
          "model": "ada",
          "max_requests_per_1_minute": 600,
          "max_tokens_per_1_minute": 150000,
          "max_images_per_1_minute": 10
        }
    ],
    "first_id": "rl-ada",
    "last_id": "rl-ada",
    "has_more": false
}
Modify project rate limit
post
 
https://api.openai.com/v1/organization/projects/{project_id}/rate_limits/{rate_limit_id}
Updates a project rate limit.

Path parameters
project_id
string

Required
The ID of the project.

rate_limit_id
string

Required
The ID of the rate limit.

Request body
batch_1_day_max_input_tokens
integer

Optional
The maximum batch input tokens per day. Only relevant for certain models.

max_audio_megabytes_per_1_minute
integer

Optional
The maximum audio megabytes per minute. Only relevant for certain models.

max_images_per_1_minute
integer

Optional
The maximum images per minute. Only relevant for certain models.

max_requests_per_1_day
integer

Optional
The maximum requests per day. Only relevant for certain models.

max_requests_per_1_minute
integer

Optional
The maximum requests per minute.

max_tokens_per_1_minute
integer

Optional
The maximum tokens per minute.

Returns
The updated ProjectRateLimit object.

Example request
curl -X POST https://api.openai.com/v1/organization/projects/proj_abc/rate_limits/rl_xxx \
  -H "Authorization: Bearer $OPENAI_ADMIN_KEY" \
  -H "Content-Type: application/json" \
  -d '{
      "max_requests_per_1_minute": 500
  }'
Response
{
    "object": "project.rate_limit",
    "id": "rl-ada",
    "model": "ada",
    "max_requests_per_1_minute": 600,
    "max_tokens_per_1_minute": 150000,
    "max_images_per_1_minute": 10
  }
The project rate limit object
Represents a project rate limit config.

batch_1_day_max_input_tokens
integer

The maximum batch input tokens per day. Only present for relevant models.

id
string

The identifier, which can be referenced in API endpoints.

max_audio_megabytes_per_1_minute
integer

The maximum audio megabytes per minute. Only present for relevant models.

max_images_per_1_minute
integer

The maximum images per minute. Only present for relevant models.

max_requests_per_1_day
integer

The maximum requests per day. Only present for relevant models.

max_requests_per_1_minute
integer

The maximum requests per minute.

max_tokens_per_1_minute
integer

The maximum tokens per minute.

model
string

The model this rate limit applies to.

object
string

The object type, which is always project.rate_limit

OBJECT The project rate limit object
{
    "object": "project.rate_limit",
    "id": "rl_ada",
    "model": "ada",
    "max_requests_per_1_minute": 600,
    "max_tokens_per_1_minute": 150000,
    "max_images_per_1_minute": 10
}
Audit logs
Logs of user actions and configuration changes within this organization. To log events, an Organization Owner must activate logging in the Data Controls Settings. Once activated, for security reasons, logging cannot be deactivated.

List audit logs
get
 
https://api.openai.com/v1/organization/audit_logs
List user actions and configuration changes within this organization.

Query parameters
actor_emails[]
array

Optional
Return only events performed by users with these emails.

actor_ids[]
array

Optional
Return only events performed by these actors. Can be a user ID, a service account ID, or an api key tracking ID.

after
string

Optional
A cursor for use in pagination. after is an object ID that defines your place in the list. For instance, if you make a list request and receive 100 objects, ending with obj_foo, your subsequent call can include after=obj_foo in order to fetch the next page of the list.

before
string

Optional
A cursor for use in pagination. before is an object ID that defines your place in the list. For instance, if you make a list request and receive 100 objects, starting with obj_foo, your subsequent call can include before=obj_foo in order to fetch the previous page of the list.

effective_at
object

Optional
Return only events whose effective_at (Unix seconds) is in this range.


Show properties
event_types[]
array

Optional
Return only events with a type in one of these values. For example, project.created. For all options, see the documentation for the audit log object.

limit
integer

Optional
Defaults to 20
A limit on the number of objects to be returned. Limit can range between 1 and 100, and the default is 20.

project_ids[]
array

Optional
Return only events for these projects.

resource_ids[]
array

Optional
Return only events performed on these targets. For example, a project ID updated.

Returns
A list of paginated Audit Log objects.

Example request
curl https://api.openai.com/v1/organization/audit_logs \
-H "Authorization: Bearer $OPENAI_ADMIN_KEY" \
-H "Content-Type: application/json"
Response
{
    "object": "list",
    "data": [
        {
            "id": "audit_log-xxx_yyyymmdd",
            "type": "project.archived",
            "effective_at": 1722461446,
            "actor": {
                "type": "api_key",
                "api_key": {
                    "type": "user",
                    "user": {
                        "id": "user-xxx",
                        "email": "user@example.com"
                    }
                }
            },
            "project.archived": {
                "id": "proj_abc"
            },
        },
        {
            "id": "audit_log-yyy__20240101",
            "type": "api_key.updated",
            "effective_at": 1720804190,
            "actor": {
                "type": "session",
                "session": {
                    "user": {
                        "id": "user-xxx",
                        "email": "user@example.com"
                    },
                    "ip_address": "127.0.0.1",
                    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                    "ja3": "a497151ce4338a12c4418c44d375173e",
                    "ja4": "q13d0313h3_55b375c5d22e_c7319ce65786",
                    "ip_address_details": {
                      "country": "US",
                      "city": "San Francisco",
                      "region": "California",
                      "region_code": "CA",
                      "asn": "1234",
                      "latitude": "37.77490",
                      "longitude": "-122.41940"
                    }
                }
            },
            "api_key.updated": {
                "id": "key_xxxx",
                "data": {
                    "scopes": ["resource_2.operation_2"]
                }
            },
        }
    ],
    "first_id": "audit_log-xxx__20240101",
    "last_id": "audit_log_yyy__20240101",
    "has_more": true
}
The audit log object
A log of a user action or configuration change within this organization.

actor
object

The actor who performed the audit logged action.


Show properties
api_key.created
object

The details for events with this type.


Show properties
api_key.deleted
object

The details for events with this type.


Show properties
api_key.updated
object

The details for events with this type.


Show properties
certificate.created
object

The details for events with this type.


Show properties
certificate.deleted
object

The details for events with this type.


Show properties
certificate.updated
object

The details for events with this type.


Show properties
certificates.activated
object

The details for events with this type.


Show properties
certificates.deactivated
object

The details for events with this type.


Show properties
checkpoint.permission.created
object

The project and fine-tuned model checkpoint that the checkpoint permission was created for.


Show properties
checkpoint.permission.deleted
object

The details for events with this type.


Show properties
effective_at
integer

The Unix timestamp (in seconds) of the event.

external_key.registered
object

The details for events with this type.


Show properties
external_key.removed
object

The details for events with this type.


Show properties
group.created
object

The details for events with this type.


Show properties
group.deleted
object

The details for events with this type.


Show properties
group.updated
object

The details for events with this type.


Show properties
id
string

The ID of this log.

invite.accepted
object

The details for events with this type.


Show properties
invite.deleted
object

The details for events with this type.


Show properties
invite.sent
object

The details for events with this type.


Show properties
ip_allowlist.config.activated
object

The details for events with this type.


Show properties
ip_allowlist.config.deactivated
object

The details for events with this type.


Show properties
ip_allowlist.created
object

The details for events with this type.


Show properties
ip_allowlist.deleted
object

The details for events with this type.


Show properties
ip_allowlist.updated
object

The details for events with this type.


Show properties
login.failed
object

The details for events with this type.


Show properties
login.succeeded
object

This event has no additional fields beyond the standard audit log attributes.

logout.failed
object

The details for events with this type.


Show properties
logout.succeeded
object

This event has no additional fields beyond the standard audit log attributes.

organization.updated
object

The details for events with this type.


Show properties
project
object

The project that the action was scoped to. Absent for actions not scoped to projects. Note that any admin actions taken via Admin API keys are associated with the default project.


Show properties
project.archived
object

The details for events with this type.


Show properties
project.created
object

The details for events with this type.


Show properties
project.deleted
object

The details for events with this type.


Show properties
project.updated
object

The details for events with this type.


Show properties
rate_limit.deleted
object

The details for events with this type.


Show properties
rate_limit.updated
object

The details for events with this type.


Show properties
role.assignment.created
object

The details for events with this type.


Show properties
role.assignment.deleted
object

The details for events with this type.


Show properties
role.created
object

The details for events with this type.


Show properties
role.deleted
object

The details for events with this type.


Show properties
role.updated
object

The details for events with this type.


Show properties
scim.disabled
object

The details for events with this type.


Show properties
scim.enabled
object

The details for events with this type.


Show properties
service_account.created
object

The details for events with this type.


Show properties
service_account.deleted
object

The details for events with this type.


Show properties
service_account.updated
object

The details for events with this type.


Show properties
type
string

The event type.

user.added
object

The details for events with this type.


Show properties
user.deleted
object

The details for events with this type.


Show properties
user.updated
object

The details for events with this type.


Show properties
OBJECT The audit log object
{
    "id": "req_xxx_20240101",
    "type": "api_key.created",
    "effective_at": 1720804090,
    "actor": {
        "type": "session",
        "session": {
            "user": {
                "id": "user-xxx",
                "email": "user@example.com"
            },
            "ip_address": "127.0.0.1",
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
    },
    "api_key.created": {
        "id": "key_xxxx",
        "data": {
            "scopes": ["resource.operation"]
        }
    }
}
Usage
The Usage API provides detailed insights into your activity across the OpenAI API. It also includes a separate Costs endpoint, which offers visibility into your spend, breaking down consumption by invoice line items and project IDs.

While the Usage API delivers granular usage data, it may not always reconcile perfectly with the Costs due to minor differences in how usage and spend are recorded. For financial purposes, we recommend using the Costs endpoint or the Costs tab in the Usage Dashboard, which will reconcile back to your billing invoice.

Completions
get
 
https://api.openai.com/v1/organization/usage/completions
Get completions usage details for the organization.

Query parameters
start_time
integer

Required
Start time (Unix seconds) of the query time range, inclusive.

api_key_ids
array

Optional
Return only usage for these API keys.

batch
boolean

Optional
If true, return batch jobs only. If false, return non-batch jobs only. By default, return both.

bucket_width
string

Optional
Defaults to 1d
Width of each time bucket in response. Currently 1m, 1h and 1d are supported, default to 1d.

end_time
integer

Optional
End time (Unix seconds) of the query time range, exclusive.

group_by
array

Optional
Group the usage data by the specified fields. Support fields include project_id, user_id, api_key_id, model, batch, service_tier or any combination of them.

limit
integer

Optional
Specifies the number of buckets to return.

bucket_width=1d: default: 7, max: 31
bucket_width=1h: default: 24, max: 168
bucket_width=1m: default: 60, max: 1440
models
array

Optional
Return only usage for these models.

page
string

Optional
A cursor for use in pagination. Corresponding to the next_page field from the previous response.

project_ids
array

Optional
Return only usage for these projects.

user_ids
array

Optional
Return only usage for these users.

Returns
A list of paginated, time bucketed Completions usage objects.

Example request
curl "https://api.openai.com/v1/organization/usage/completions?start_time=1730419200&limit=1" \
-H "Authorization: Bearer $OPENAI_ADMIN_KEY" \
-H "Content-Type: application/json"
Response
{
    "object": "page",
    "data": [
        {
            "object": "bucket",
            "start_time": 1730419200,
            "end_time": 1730505600,
            "results": [
                {
                    "object": "organization.usage.completions.result",
                    "input_tokens": 1000,
                    "output_tokens": 500,
                    "input_cached_tokens": 800,
                    "input_audio_tokens": 0,
                    "output_audio_tokens": 0,
                    "num_model_requests": 5,
                    "project_id": null,
                    "user_id": null,
                    "api_key_id": null,
                    "model": null,
                    "batch": null,
                    "service_tier": null
                }
            ]
        }
    ],
    "has_more": true,
    "next_page": "page_AAAAAGdGxdEiJdKOAAAAAGcqsYA="
}
Completions usage object
The aggregated completions usage details of the specific time bucket.

api_key_id
string

When group_by=api_key_id, this field provides the API key ID of the grouped usage result.

batch
boolean

When group_by=batch, this field tells whether the grouped usage result is batch or not.

input_audio_tokens
integer

The aggregated number of audio input tokens used, including cached tokens.

input_cached_tokens
integer

The aggregated number of text input tokens that has been cached from previous requests. For customers subscribe to scale tier, this includes scale tier tokens.

input_tokens
integer

The aggregated number of text input tokens used, including cached tokens. For customers subscribe to scale tier, this includes scale tier tokens.

model
string

When group_by=model, this field provides the model name of the grouped usage result.

num_model_requests
integer

The count of requests made to the model.

object
string

output_audio_tokens
integer

The aggregated number of audio output tokens used.

output_tokens
integer

The aggregated number of text output tokens used. For customers subscribe to scale tier, this includes scale tier tokens.

project_id
string

When group_by=project_id, this field provides the project ID of the grouped usage result.

service_tier
string

When group_by=service_tier, this field provides the service tier of the grouped usage result.

user_id
string

When group_by=user_id, this field provides the user ID of the grouped usage result.

OBJECT Completions usage object
{
    "object": "organization.usage.completions.result",
    "input_tokens": 5000,
    "output_tokens": 1000,
    "input_cached_tokens": 4000,
    "input_audio_tokens": 300,
    "output_audio_tokens": 200,
    "num_model_requests": 5,
    "project_id": "proj_abc",
    "user_id": "user-abc",
    "api_key_id": "key_abc",
    "model": "gpt-4o-mini-2024-07-18",
    "batch": false,
    "service_tier": "default"
}
Embeddings
get
 
https://api.openai.com/v1/organization/usage/embeddings
Get embeddings usage details for the organization.

Query parameters
start_time
integer

Required
Start time (Unix seconds) of the query time range, inclusive.

api_key_ids
array

Optional
Return only usage for these API keys.

bucket_width
string

Optional
Defaults to 1d
Width of each time bucket in response. Currently 1m, 1h and 1d are supported, default to 1d.

end_time
integer

Optional
End time (Unix seconds) of the query time range, exclusive.

group_by
array

Optional
Group the usage data by the specified fields. Support fields include project_id, user_id, api_key_id, model or any combination of them.

limit
integer

Optional
Specifies the number of buckets to return.

bucket_width=1d: default: 7, max: 31
bucket_width=1h: default: 24, max: 168
bucket_width=1m: default: 60, max: 1440
models
array

Optional
Return only usage for these models.

page
string

Optional
A cursor for use in pagination. Corresponding to the next_page field from the previous response.

project_ids
array

Optional
Return only usage for these projects.

user_ids
array

Optional
Return only usage for these users.

Returns
A list of paginated, time bucketed Embeddings usage objects.

Example request
curl "https://api.openai.com/v1/organization/usage/embeddings?start_time=1730419200&limit=1" \
-H "Authorization: Bearer $OPENAI_ADMIN_KEY" \
-H "Content-Type: application/json"
Response
{
    "object": "page",
    "data": [
        {
            "object": "bucket",
            "start_time": 1730419200,
            "end_time": 1730505600,
            "results": [
                {
                    "object": "organization.usage.embeddings.result",
                    "input_tokens": 16,
                    "num_model_requests": 2,
                    "project_id": null,
                    "user_id": null,
                    "api_key_id": null,
                    "model": null
                }
            ]
        }
    ],
    "has_more": false,
    "next_page": null
}
Embeddings usage object
The aggregated embeddings usage details of the specific time bucket.

api_key_id
string

When group_by=api_key_id, this field provides the API key ID of the grouped usage result.

input_tokens
integer

The aggregated number of input tokens used.

model
string

When group_by=model, this field provides the model name of the grouped usage result.

num_model_requests
integer

The count of requests made to the model.

object
string

project_id
string

When group_by=project_id, this field provides the project ID of the grouped usage result.

user_id
string

When group_by=user_id, this field provides the user ID of the grouped usage result.

OBJECT Embeddings usage object
{
    "object": "organization.usage.embeddings.result",
    "input_tokens": 20,
    "num_model_requests": 2,
    "project_id": "proj_abc",
    "user_id": "user-abc",
    "api_key_id": "key_abc",
    "model": "text-embedding-ada-002-v2"
}
Moderations
get
 
https://api.openai.com/v1/organization/usage/moderations
Get moderations usage details for the organization.

Query parameters
start_time
integer

Required
Start time (Unix seconds) of the query time range, inclusive.

api_key_ids
array

Optional
Return only usage for these API keys.

bucket_width
string

Optional
Defaults to 1d
Width of each time bucket in response. Currently 1m, 1h and 1d are supported, default to 1d.

end_time
integer

Optional
End time (Unix seconds) of the query time range, exclusive.

group_by
array

Optional
Group the usage data by the specified fields. Support fields include project_id, user_id, api_key_id, model or any combination of them.

limit
integer

Optional
Specifies the number of buckets to return.

bucket_width=1d: default: 7, max: 31
bucket_width=1h: default: 24, max: 168
bucket_width=1m: default: 60, max: 1440
models
array

Optional
Return only usage for these models.

page
string

Optional
A cursor for use in pagination. Corresponding to the next_page field from the previous response.

project_ids
array

Optional
Return only usage for these projects.

user_ids
array

Optional
Return only usage for these users.

Returns
A list of paginated, time bucketed Moderations usage objects.

Example request
curl "https://api.openai.com/v1/organization/usage/moderations?start_time=1730419200&limit=1" \
-H "Authorization: Bearer $OPENAI_ADMIN_KEY" \
-H "Content-Type: application/json"
Response
{
    "object": "page",
    "data": [
        {
            "object": "bucket",
            "start_time": 1730419200,
            "end_time": 1730505600,
            "results": [
                {
                    "object": "organization.usage.moderations.result",
                    "input_tokens": 16,
                    "num_model_requests": 2,
                    "project_id": null,
                    "user_id": null,
                    "api_key_id": null,
                    "model": null
                }
            ]
        }
    ],
    "has_more": false,
    "next_page": null
}
Moderations usage object
The aggregated moderations usage details of the specific time bucket.

api_key_id
string

When group_by=api_key_id, this field provides the API key ID of the grouped usage result.

input_tokens
integer

The aggregated number of input tokens used.

model
string

When group_by=model, this field provides the model name of the grouped usage result.

num_model_requests
integer

The count of requests made to the model.

object
string

project_id
string

When group_by=project_id, this field provides the project ID of the grouped usage result.

user_id
string

When group_by=user_id, this field provides the user ID of the grouped usage result.

OBJECT Moderations usage object
{
    "object": "organization.usage.moderations.result",
    "input_tokens": 20,
    "num_model_requests": 2,
    "project_id": "proj_abc",
    "user_id": "user-abc",
    "api_key_id": "key_abc",
    "model": "text-moderation"
}
Images
get
 
https://api.openai.com/v1/organization/usage/images
Get images usage details for the organization.

Query parameters
start_time
integer

Required
Start time (Unix seconds) of the query time range, inclusive.

api_key_ids
array

Optional
Return only usage for these API keys.

bucket_width
string

Optional
Defaults to 1d
Width of each time bucket in response. Currently 1m, 1h and 1d are supported, default to 1d.

end_time
integer

Optional
End time (Unix seconds) of the query time range, exclusive.

group_by
array

Optional
Group the usage data by the specified fields. Support fields include project_id, user_id, api_key_id, model, size, source or any combination of them.

limit
integer

Optional
Specifies the number of buckets to return.

bucket_width=1d: default: 7, max: 31
bucket_width=1h: default: 24, max: 168
bucket_width=1m: default: 60, max: 1440
models
array

Optional
Return only usage for these models.

page
string

Optional
A cursor for use in pagination. Corresponding to the next_page field from the previous response.

project_ids
array

Optional
Return only usage for these projects.

sizes
array

Optional
Return only usages for these image sizes. Possible values are 256x256, 512x512, 1024x1024, 1792x1792, 1024x1792 or any combination of them.

sources
array

Optional
Return only usages for these sources. Possible values are image.generation, image.edit, image.variation or any combination of them.

user_ids
array

Optional
Return only usage for these users.

Returns
A list of paginated, time bucketed Images usage objects.

Example request
curl "https://api.openai.com/v1/organization/usage/images?start_time=1730419200&limit=1" \
-H "Authorization: Bearer $OPENAI_ADMIN_KEY" \
-H "Content-Type: application/json"
Response
{
    "object": "page",
    "data": [
        {
            "object": "bucket",
            "start_time": 1730419200,
            "end_time": 1730505600,
            "results": [
                {
                    "object": "organization.usage.images.result",
                    "images": 2,
                    "num_model_requests": 2,
                    "size": null,
                    "source": null,
                    "project_id": null,
                    "user_id": null,
                    "api_key_id": null,
                    "model": null
                }
            ]
        }
    ],
    "has_more": false,
    "next_page": null
}
Images usage object
The aggregated images usage details of the specific time bucket.

api_key_id
string

When group_by=api_key_id, this field provides the API key ID of the grouped usage result.

images
integer

The number of images processed.

model
string

When group_by=model, this field provides the model name of the grouped usage result.

num_model_requests
integer

The count of requests made to the model.

object
string

project_id
string

When group_by=project_id, this field provides the project ID of the grouped usage result.

size
string

When group_by=size, this field provides the image size of the grouped usage result.

source
string

When group_by=source, this field provides the source of the grouped usage result, possible values are image.generation, image.edit, image.variation.

user_id
string

When group_by=user_id, this field provides the user ID of the grouped usage result.

OBJECT Images usage object
{
    "object": "organization.usage.images.result",
    "images": 2,
    "num_model_requests": 2,
    "size": "1024x1024",
    "source": "image.generation",
    "project_id": "proj_abc",
    "user_id": "user-abc",
    "api_key_id": "key_abc",
    "model": "dall-e-3"
}
Audio speeches
get
 
https://api.openai.com/v1/organization/usage/audio_speeches
Get audio speeches usage details for the organization.

Query parameters
start_time
integer

Required
Start time (Unix seconds) of the query time range, inclusive.

api_key_ids
array

Optional
Return only usage for these API keys.

bucket_width
string

Optional
Defaults to 1d
Width of each time bucket in response. Currently 1m, 1h and 1d are supported, default to 1d.

end_time
integer

Optional
End time (Unix seconds) of the query time range, exclusive.

group_by
array

Optional
Group the usage data by the specified fields. Support fields include project_id, user_id, api_key_id, model or any combination of them.

limit
integer

Optional
Specifies the number of buckets to return.

bucket_width=1d: default: 7, max: 31
bucket_width=1h: default: 24, max: 168
bucket_width=1m: default: 60, max: 1440
models
array

Optional
Return only usage for these models.

page
string

Optional
A cursor for use in pagination. Corresponding to the next_page field from the previous response.

project_ids
array

Optional
Return only usage for these projects.

user_ids
array

Optional
Return only usage for these users.

Returns
A list of paginated, time bucketed Audio speeches usage objects.

Example request
curl "https://api.openai.com/v1/organization/usage/audio_speeches?start_time=1730419200&limit=1" \
-H "Authorization: Bearer $OPENAI_ADMIN_KEY" \
-H "Content-Type: application/json"
Response
{
    "object": "page",
    "data": [
        {
            "object": "bucket",
            "start_time": 1730419200,
            "end_time": 1730505600,
            "results": [
                {
                    "object": "organization.usage.audio_speeches.result",
                    "characters": 45,
                    "num_model_requests": 1,
                    "project_id": null,
                    "user_id": null,
                    "api_key_id": null,
                    "model": null
                }
            ]
        }
    ],
    "has_more": false,
    "next_page": null
}
Audio speeches usage object
The aggregated audio speeches usage details of the specific time bucket.

api_key_id
string

When group_by=api_key_id, this field provides the API key ID of the grouped usage result.

characters
integer

The number of characters processed.

model
string

When group_by=model, this field provides the model name of the grouped usage result.

num_model_requests
integer

The count of requests made to the model.

object
string

project_id
string

When group_by=project_id, this field provides the project ID of the grouped usage result.

user_id
string

When group_by=user_id, this field provides the user ID of the grouped usage result.

OBJECT Audio speeches usage object
{
    "object": "organization.usage.audio_speeches.result",
    "characters": 45,
    "num_model_requests": 1,
    "project_id": "proj_abc",
    "user_id": "user-abc",
    "api_key_id": "key_abc",
    "model": "tts-1"
}
Audio transcriptions
get
 
https://api.openai.com/v1/organization/usage/audio_transcriptions
Get audio transcriptions usage details for the organization.

Query parameters
start_time
integer

Required
Start time (Unix seconds) of the query time range, inclusive.

api_key_ids
array

Optional
Return only usage for these API keys.

bucket_width
string

Optional
Defaults to 1d
Width of each time bucket in response. Currently 1m, 1h and 1d are supported, default to 1d.

end_time
integer

Optional
End time (Unix seconds) of the query time range, exclusive.

group_by
array

Optional
Group the usage data by the specified fields. Support fields include project_id, user_id, api_key_id, model or any combination of them.

limit
integer

Optional
Specifies the number of buckets to return.

bucket_width=1d: default: 7, max: 31
bucket_width=1h: default: 24, max: 168
bucket_width=1m: default: 60, max: 1440
models
array

Optional
Return only usage for these models.

page
string

Optional
A cursor for use in pagination. Corresponding to the next_page field from the previous response.

project_ids
array

Optional
Return only usage for these projects.

user_ids
array

Optional
Return only usage for these users.

Returns
A list of paginated, time bucketed Audio transcriptions usage objects.

Example request
curl "https://api.openai.com/v1/organization/usage/audio_transcriptions?start_time=1730419200&limit=1" \
-H "Authorization: Bearer $OPENAI_ADMIN_KEY" \
-H "Content-Type: application/json"
Response
{
    "object": "page",
    "data": [
        {
            "object": "bucket",
            "start_time": 1730419200,
            "end_time": 1730505600,
            "results": [
                {
                    "object": "organization.usage.audio_transcriptions.result",
                    "seconds": 20,
                    "num_model_requests": 1,
                    "project_id": null,
                    "user_id": null,
                    "api_key_id": null,
                    "model": null
                }
            ]
        }
    ],
    "has_more": false,
    "next_page": null
}
Audio transcriptions usage object
The aggregated audio transcriptions usage details of the specific time bucket.

api_key_id
string

When group_by=api_key_id, this field provides the API key ID of the grouped usage result.

model
string

When group_by=model, this field provides the model name of the grouped usage result.

num_model_requests
integer

The count of requests made to the model.

object
string

project_id
string

When group_by=project_id, this field provides the project ID of the grouped usage result.

seconds
integer

The number of seconds processed.

user_id
string

When group_by=user_id, this field provides the user ID of the grouped usage result.

OBJECT Audio transcriptions usage object
{
    "object": "organization.usage.audio_transcriptions.result",
    "seconds": 10,
    "num_model_requests": 1,
    "project_id": "proj_abc",
    "user_id": "user-abc",
    "api_key_id": "key_abc",
    "model": "tts-1"
}
Vector stores
get
 
https://api.openai.com/v1/organization/usage/vector_stores
Get vector stores usage details for the organization.

Query parameters
start_time
integer

Required
Start time (Unix seconds) of the query time range, inclusive.

bucket_width
string

Optional
Defaults to 1d
Width of each time bucket in response. Currently 1m, 1h and 1d are supported, default to 1d.

end_time
integer

Optional
End time (Unix seconds) of the query time range, exclusive.

group_by
array

Optional
Group the usage data by the specified fields. Support fields include project_id.

limit
integer

Optional
Specifies the number of buckets to return.

bucket_width=1d: default: 7, max: 31
bucket_width=1h: default: 24, max: 168
bucket_width=1m: default: 60, max: 1440
page
string

Optional
A cursor for use in pagination. Corresponding to the next_page field from the previous response.

project_ids
array

Optional
Return only usage for these projects.

Returns
A list of paginated, time bucketed Vector stores usage objects.

Example request
curl "https://api.openai.com/v1/organization/usage/vector_stores?start_time=1730419200&limit=1" \
-H "Authorization: Bearer $OPENAI_ADMIN_KEY" \
-H "Content-Type: application/json"
Response
{
    "object": "page",
    "data": [
        {
            "object": "bucket",
            "start_time": 1730419200,
            "end_time": 1730505600,
            "results": [
                {
                    "object": "organization.usage.vector_stores.result",
                    "usage_bytes": 1024,
                    "project_id": null
                }
            ]
        }
    ],
    "has_more": false,
    "next_page": null
}
Vector stores usage object
The aggregated vector stores usage details of the specific time bucket.

object
string

project_id
string

When group_by=project_id, this field provides the project ID of the grouped usage result.

usage_bytes
integer

The vector stores usage in bytes.

OBJECT Vector stores usage object
{
    "object": "organization.usage.vector_stores.result",
    "usage_bytes": 1024,
    "project_id": "proj_abc"
}
Code interpreter sessions
get
 
https://api.openai.com/v1/organization/usage/code_interpreter_sessions
Get code interpreter sessions usage details for the organization.

Query parameters
start_time
integer

Required
Start time (Unix seconds) of the query time range, inclusive.

bucket_width
string

Optional
Defaults to 1d
Width of each time bucket in response. Currently 1m, 1h and 1d are supported, default to 1d.

end_time
integer

Optional
End time (Unix seconds) of the query time range, exclusive.

group_by
array

Optional
Group the usage data by the specified fields. Support fields include project_id.

limit
integer

Optional
Specifies the number of buckets to return.

bucket_width=1d: default: 7, max: 31
bucket_width=1h: default: 24, max: 168
bucket_width=1m: default: 60, max: 1440
page
string

Optional
A cursor for use in pagination. Corresponding to the next_page field from the previous response.

project_ids
array

Optional
Return only usage for these projects.

Returns
A list of paginated, time bucketed Code interpreter sessions usage objects.

Example request
curl "https://api.openai.com/v1/organization/usage/code_interpreter_sessions?start_time=1730419200&limit=1" \
-H "Authorization: Bearer $OPENAI_ADMIN_KEY" \
-H "Content-Type: application/json"
Response
{
    "object": "page",
    "data": [
        {
            "object": "bucket",
            "start_time": 1730419200,
            "end_time": 1730505600,
            "results": [
                {
                    "object": "organization.usage.code_interpreter_sessions.result",
                    "num_sessions": 1,
                    "project_id": null
                }
            ]
        }
    ],
    "has_more": false,
    "next_page": null
}
Code interpreter sessions usage object
The aggregated code interpreter sessions usage details of the specific time bucket.

num_sessions
integer

The number of code interpreter sessions.

object
string

project_id
string

When group_by=project_id, this field provides the project ID of the grouped usage result.

OBJECT Code interpreter sessions usage object
{
    "object": "organization.usage.code_interpreter_sessions.result",
    "num_sessions": 1,
    "project_id": "proj_abc"
}
Costs
get
 
https://api.openai.com/v1/organization/costs
Get costs details for the organization.

Query parameters
start_time
integer

Required
Start time (Unix seconds) of the query time range, inclusive.

bucket_width
string

Optional
Defaults to 1d
Width of each time bucket in response. Currently only 1d is supported, default to 1d.

end_time
integer

Optional
End time (Unix seconds) of the query time range, exclusive.

group_by
array

Optional
Group the costs by the specified fields. Support fields include project_id, line_item and any combination of them.

limit
integer

Optional
Defaults to 7
A limit on the number of buckets to be returned. Limit can range between 1 and 180, and the default is 7.

page
string

Optional
A cursor for use in pagination. Corresponding to the next_page field from the previous response.

project_ids
array

Optional
Return only costs for these projects.

Returns
A list of paginated, time bucketed Costs objects.

Example request
curl "https://api.openai.com/v1/organization/costs?start_time=1730419200&limit=1" \
-H "Authorization: Bearer $OPENAI_ADMIN_KEY" \
-H "Content-Type: application/json"
Response
{
    "object": "page",
    "data": [
        {
            "object": "bucket",
            "start_time": 1730419200,
            "end_time": 1730505600,
            "results": [
                {
                    "object": "organization.costs.result",
                    "amount": {
                        "value": 0.06,
                        "currency": "usd"
                    },
                    "line_item": null,
                    "project_id": null
                }
            ]
        }
    ],
    "has_more": false,
    "next_page": null
}
Costs object
The aggregated costs details of the specific time bucket.

amount
object

The monetary value in its associated currency.


Show properties
line_item
string

When group_by=line_item, this field provides the line item of the grouped costs result.

object
string

project_id
string

When group_by=project_id, this field provides the project ID of the grouped costs result.

OBJECT Costs object
{
    "object": "organization.costs.result",
    "amount": {
      "value": 0.06,
      "currency": "usd"
    },
    "line_item": "Image models",
    "project_id": "proj_abc"
}
Certificates
Beta
Manage Mutual TLS certificates across your organization and projects.

Learn more about Mutual TLS.

Upload certificate
post
 
https://api.openai.com/v1/organization/certificates
Upload a certificate to the organization. This does not automatically activate the certificate.

Organizations can upload up to 50 certificates.

Request body
content
string

Required
The certificate content in PEM format

name
string

Optional
An optional name for the certificate

Returns
A single Certificate object.

Example request
curl -X POST https://api.openai.com/v1/organization/certificates \
-H "Authorization: Bearer $OPENAI_ADMIN_KEY" \
-H "Content-Type: application/json" \
-d '{
  "name": "My Example Certificate",
  "certificate": "-----BEGIN CERTIFICATE-----\\nMIIDeT...\\n-----END CERTIFICATE-----"
}'
Response
{
  "object": "certificate",
  "id": "cert_abc",
  "name": "My Example Certificate",
  "created_at": 1234567,
  "certificate_details": {
    "valid_at": 12345667,
    "expires_at": 12345678
  }
}
Get certificate
get
 
https://api.openai.com/v1/organization/certificates/{certificate_id}
Get a certificate that has been uploaded to the organization.

You can get a certificate regardless of whether it is active or not.

Path parameters
certificate_id
string

Required
Unique ID of the certificate to retrieve.

Query parameters
include
array

Optional
A list of additional fields to include in the response. Currently the only supported value is content to fetch the PEM content of the certificate.

Returns
A single Certificate object.

Example request
curl "https://api.openai.com/v1/organization/certificates/cert_abc?include[]=content" \
-H "Authorization: Bearer $OPENAI_ADMIN_KEY"
Response
{
  "object": "certificate",
  "id": "cert_abc",
  "name": "My Example Certificate",
  "created_at": 1234567,
  "certificate_details": {
    "valid_at": 1234567,
    "expires_at": 12345678,
    "content": "-----BEGIN CERTIFICATE-----MIIDeT...-----END CERTIFICATE-----"
  }
}
Modify certificate
post
 
https://api.openai.com/v1/organization/certificates/{certificate_id}
Modify a certificate. Note that only the name can be modified.

Request body
name
string

Required
The updated name for the certificate

Returns
The updated Certificate object.

Example request
curl -X POST https://api.openai.com/v1/organization/certificates/cert_abc \
-H "Authorization: Bearer $OPENAI_ADMIN_KEY" \
-H "Content-Type: application/json" \
-d '{
  "name": "Renamed Certificate"
}'
Response
{
  "object": "certificate",
  "id": "cert_abc",
  "name": "Renamed Certificate",
  "created_at": 1234567,
  "certificate_details": {
    "valid_at": 12345667,
    "expires_at": 12345678
  }
}
Delete certificate
delete
 
https://api.openai.com/v1/organization/certificates/{certificate_id}
Delete a certificate from the organization.

The certificate must be inactive for the organization and all projects.

Returns
A confirmation object indicating the certificate was deleted.

Example request
curl -X DELETE https://api.openai.com/v1/organization/certificates/cert_abc \
-H "Authorization: Bearer $OPENAI_ADMIN_KEY"
Response
{
  "object": "certificate.deleted",
  "id": "cert_abc"
}
List organization certificates
get
 
https://api.openai.com/v1/organization/certificates
List uploaded certificates for this organization.

Query parameters
after
string

Optional
A cursor for use in pagination. after is an object ID that defines your place in the list. For instance, if you make a list request and receive 100 objects, ending with obj_foo, your subsequent call can include after=obj_foo in order to fetch the next page of the list.

limit
integer

Optional
Defaults to 20
A limit on the number of objects to be returned. Limit can range between 1 and 100, and the default is 20.

order
string

Optional
Defaults to desc
Sort order by the created_at timestamp of the objects. asc for ascending order and desc for descending order.

Returns
A list of Certificate objects.

Example request
curl https://api.openai.com/v1/organization/certificates \
-H "Authorization: Bearer $OPENAI_ADMIN_KEY"
Response
{
  "object": "list",
  "data": [
    {
      "object": "organization.certificate",
      "id": "cert_abc",
      "name": "My Example Certificate",
      "active": true,
      "created_at": 1234567,
      "certificate_details": {
        "valid_at": 12345667,
        "expires_at": 12345678
      }
    },
  ],
  "first_id": "cert_abc",
  "last_id": "cert_abc",
  "has_more": false
}
List project certificates
get
 
https://api.openai.com/v1/organization/projects/{project_id}/certificates
List certificates for this project.

Path parameters
project_id
string

Required
The ID of the project.

Query parameters
after
string

Optional
A cursor for use in pagination. after is an object ID that defines your place in the list. For instance, if you make a list request and receive 100 objects, ending with obj_foo, your subsequent call can include after=obj_foo in order to fetch the next page of the list.

limit
integer

Optional
Defaults to 20
A limit on the number of objects to be returned. Limit can range between 1 and 100, and the default is 20.

order
string

Optional
Defaults to desc
Sort order by the created_at timestamp of the objects. asc for ascending order and desc for descending order.

Returns
A list of Certificate objects.

Example request
curl https://api.openai.com/v1/organization/projects/proj_abc/certificates \
-H "Authorization: Bearer $OPENAI_ADMIN_KEY"
Response
{
  "object": "list",
  "data": [
    {
      "object": "organization.project.certificate",
      "id": "cert_abc",
      "name": "My Example Certificate",
      "active": true,
      "created_at": 1234567,
      "certificate_details": {
        "valid_at": 12345667,
        "expires_at": 12345678
      }
    },
  ],
  "first_id": "cert_abc",
  "last_id": "cert_abc",
  "has_more": false
}
Activate certificates for organization
post
 
https://api.openai.com/v1/organization/certificates/activate
Activate certificates at the organization level.

You can atomically and idempotently activate up to 10 certificates at a time.

Request body
certificate_ids
array

Required
Returns
A list of Certificate objects that were activated.

Example request
curl https://api.openai.com/v1/organization/certificates/activate \
-H "Authorization: Bearer $OPENAI_ADMIN_KEY" \
-H "Content-Type: application/json" \
-d '{
  "data": ["cert_abc", "cert_def"]
}'
Response
{
  "object": "organization.certificate.activation",
  "data": [
    {
      "object": "organization.certificate",
      "id": "cert_abc",
      "name": "My Example Certificate",
      "active": true,
      "created_at": 1234567,
      "certificate_details": {
        "valid_at": 12345667,
        "expires_at": 12345678
      }
    },
    {
      "object": "organization.certificate",
      "id": "cert_def",
      "name": "My Example Certificate 2",
      "active": true,
      "created_at": 1234567,
      "certificate_details": {
        "valid_at": 12345667,
        "expires_at": 12345678
      }
    },
  ],
}
Deactivate certificates for organization
post
 
https://api.openai.com/v1/organization/certificates/deactivate
Deactivate certificates at the organization level.

You can atomically and idempotently deactivate up to 10 certificates at a time.

Request body
certificate_ids
array

Required
Returns
A list of Certificate objects that were deactivated.

Example request
curl https://api.openai.com/v1/organization/certificates/deactivate \
-H "Authorization: Bearer $OPENAI_ADMIN_KEY" \
-H "Content-Type: application/json" \
-d '{
  "data": ["cert_abc", "cert_def"]
}'
Response
{
  "object": "organization.certificate.deactivation",
  "data": [
    {
      "object": "organization.certificate",
      "id": "cert_abc",
      "name": "My Example Certificate",
      "active": false,
      "created_at": 1234567,
      "certificate_details": {
        "valid_at": 12345667,
        "expires_at": 12345678
      }
    },
    {
      "object": "organization.certificate",
      "id": "cert_def",
      "name": "My Example Certificate 2",
      "active": false,
      "created_at": 1234567,
      "certificate_details": {
        "valid_at": 12345667,
        "expires_at": 12345678
      }
    },
  ],
}
Activate certificates for project
post
 
https://api.openai.com/v1/organization/projects/{project_id}/certificates/activate
Activate certificates at the project level.

You can atomically and idempotently activate up to 10 certificates at a time.

Path parameters
project_id
string

Required
The ID of the project.

Request body
certificate_ids
array

Required
Returns
A list of Certificate objects that were activated.

Example request
curl https://api.openai.com/v1/organization/projects/proj_abc/certificates/activate \
-H "Authorization: Bearer $OPENAI_ADMIN_KEY" \
-H "Content-Type: application/json" \
-d '{
  "data": ["cert_abc", "cert_def"]
}'
Response
{
  "object": "organization.project.certificate.activation",
  "data": [
    {
      "object": "organization.project.certificate",
      "id": "cert_abc",
      "name": "My Example Certificate",
      "active": true,
      "created_at": 1234567,
      "certificate_details": {
        "valid_at": 12345667,
        "expires_at": 12345678
      }
    },
    {
      "object": "organization.project.certificate",
      "id": "cert_def",
      "name": "My Example Certificate 2",
      "active": true,
      "created_at": 1234567,
      "certificate_details": {
        "valid_at": 12345667,
        "expires_at": 12345678
      }
    },
  ],
}
Deactivate certificates for project
post
 
https://api.openai.com/v1/organization/projects/{project_id}/certificates/deactivate
Deactivate certificates at the project level. You can atomically and idempotently deactivate up to 10 certificates at a time.

Path parameters
project_id
string

Required
The ID of the project.

Request body
certificate_ids
array

Required
Returns
A list of Certificate objects that were deactivated.

Example request
curl https://api.openai.com/v1/organization/projects/proj_abc/certificates/deactivate \
-H "Authorization: Bearer $OPENAI_ADMIN_KEY" \
-H "Content-Type: application/json" \
-d '{
  "data": ["cert_abc", "cert_def"]
}'
Response
{
  "object": "organization.project.certificate.deactivation",
  "data": [
    {
      "object": "organization.project.certificate",
      "id": "cert_abc",
      "name": "My Example Certificate",
      "active": false,
      "created_at": 1234567,
      "certificate_details": {
        "valid_at": 12345667,
        "expires_at": 12345678
      }
    },
    {
      "object": "organization.project.certificate",
      "id": "cert_def",
      "name": "My Example Certificate 2",
      "active": false,
      "created_at": 1234567,
      "certificate_details": {
        "valid_at": 12345667,
        "expires_at": 12345678
      }
    },
  ],
}
The certificate object
Represents an individual certificate uploaded to the organization.

active
boolean

Whether the certificate is currently active at the specified scope. Not returned when getting details for a specific certificate.

certificate_details
object


Show properties
created_at
integer

The Unix timestamp (in seconds) of when the certificate was uploaded.

id
string

The identifier, which can be referenced in API endpoints

name
string

The name of the certificate.

object
string

The object type.

If creating, updating, or getting a specific certificate, the object type is certificate.
If listing, activating, or deactivating certificates for the organization, the object type is organization.certificate.
If listing, activating, or deactivating certificates for a project, the object type is organization.project.certificate.