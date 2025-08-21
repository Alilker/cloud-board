# Cloud-Board (A CS50x final project)

#### Video Demo: <youtube.com>
#### Description:
Cloud-Board is a simple kanban board centered team-management and organization platform. It makes collaboration easy with its intuitive design and user-friendly visual interface for managing tasks and projects. (A CS50x final project!)


## Features
- Team and topic specific kanban boards for members to collaborate seamlessly
- Simple, non-cluttered UI and UX
- Intuitive team creating and managing interface
- Privilege-based access control for teams
- Explore page for finding new and exciting open-source projects
- Real-time database updates for absolute synchronization
- Responsive real-time feedback for user account actions
- Error modal for displaying input-related errors
- Pagination for necessary pages


## Page Information

#### 1. Index

The index page is the main landing page for users. Key elements include:

* Dynamic index page based on whether the user is logged in
* A non-logged in page that shows the concept of the site and buttons to register or log in
* A logged in page that acts as a quick menu for the main capabilities of the site

#### 2. Login 

The login page allows previously registered users are able to log in to their account. Key elements include:

* Users can input their username and password to log in.
* Real-time validation feedback for user input.

#### 3. Register

The register page allows users to create accounts. Key elements include:

* User input fields for username, password, and a confirmation
* Real-time validation feedback for user input

#### 4. Account

The account page allows logged in users to change their username and/or their password. Key elements include:

* User input fields for new username, new password, new password confirmation, and current password
* Users can selectively change their usernname or password, or both
* Real-time validation feedback for user input

#### 5. Explore

The explore page allows users to find new open-source projects to join and contribute to. Key elements include:

* Search field for users to find specific teams
* Join button for each team which allows users to directly join the team

#### 6. Teams

The teams page allows users to view the teams they are apart of. Key elements include:

* Specific seperation for teams user is just a member of, and is an editor / admin of
* Team information for team cards
* Management related buttons for privilege specific dashboards
* One click buttons to view teams
* Pagination for team cards
* Buttons to join teams with a name and or team code

### 7. Manage Team Dashboard

The manage team dashboard allows team admins to manage team information and team members. Key elements include:

* Manage team form that allows admins to edit team information such as team name, status, code, and description
* Manage users form that allows admins to look up specific users, and edit their privilege in the team
> Batch processing for user management isn't available so users have a button next to them indicating that they are to be edited
* Delete team button that allows admins to delete the team completely. The form requires specific 'DELETE' input to be submitted

### 8. Edit Team Dashboard

The edit team dashboard allows both team admins and team editors to edit team's topics. Key elements include:

* Create topic button that allows editors and admins to create a new topic
* Edit topic button that allows editors and admins to select a specific topic and edit its name
> Batch processing for topic editting isn't available so topics have a button next to them indicating that they are to be edited

### 9. Team Page

The team page allows users to view a teams topics

### 10. Team Board

The team board page allows users to see the board of a topic of a team they are apart of. Key elements include:

* Drag and drop functionality for users to move around notes
* Specific delete column and add note buttons for only admins and editors to view and access
* Add button allows editors and admins to add a new note to the desired column
* Delete column is for editors and admins to drag notes on top of it and have deleted
* Edit note modal that allows editors and admins to click on, and edit the contents of the note
* Announcements column that only editors and admins can drag and drop from


## Getting Started

### 1. Clone the repository:

    git clone https://github.com/alilker/cloudboard.git


### 2. Install dependencies:

    pip install -r requirements.txt

### 3. Initialize the database:

    sqlite3 database.db ".read schema.sql"

### 4. Create a .env file with the following format

    SECRET_KEY=YOUR_SECRET_KEY_HERE

### 5. Run the app:

    python app.py


## License

See [LICENCE](LICENSE) for details


--- 
# This was Cloud-Board, a CS50x final project :)