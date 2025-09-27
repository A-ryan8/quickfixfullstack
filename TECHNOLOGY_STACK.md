# Our Technology Stack

## **1. Frontend (Citizen App)**
* **Flutter:** Flutter serves as our cross-platform framework for building native iOS and Android applications from a single codebase. This choice provides significant benefits including rapid development, consistent user experience across platforms, and native performance. Flutter's widget-based architecture allows us to create a modern, responsive UI that works seamlessly on both mobile platforms while maintaining a single codebase for easier maintenance and updates.

* **Dart:** The programming language powering our Flutter applications, providing strong typing and excellent performance for mobile development.

* **Key Flutter Packages:**
  - `image_picker`: Enables camera and gallery access for photo/video capture
  - `geolocator` & `geocoding`: Provides GPS location services and address resolution
  - `permission_handler`: Manages device permissions for camera, location, and storage
  - `video_player`: Handles video playback functionality
  - `path_provider`: Manages file system access for storing generated PDFs
  - `pdf` & `printing`: Generates and prints PDF reports of complaints
  - `open_file`: Opens generated PDF files in external applications
  - `http`: Handles HTTP requests to our backend APIs

## **2. Frontend (Admin Dashboard)**
* **React:** React serves as our JavaScript library for building the dynamic, high-performance user interface for the web-based admin dashboard. React's component-based architecture allows us to create reusable UI elements and manage complex state efficiently. The virtual DOM ensures optimal performance when rendering large lists of complaints and real-time updates.

* **Vite:** Our modern build tool and development server, providing lightning-fast hot module replacement and optimized production builds.

* **Key React Libraries:**
  - **Material-UI (MUI):** Provides a comprehensive set of pre-built, accessible React components following Google's Material Design principles. We use MUI for consistent styling, data grids, icons, and form controls.
  - **React Router DOM:** Handles client-side routing and navigation between different dashboard pages.
  - **Axios:** Manages HTTP requests to our FastAPI backend with interceptors for authentication.
  - **React Leaflet:** Integrates interactive maps using the Leaflet mapping library for visualizing complaint locations.
  - **Recharts:** Creates interactive charts and graphs for analytics and reporting.
  - **React i18next:** Provides internationalization support for multiple languages.
  - **React Toastify:** Displays user-friendly notification messages.

* **Styling:**
  - **Tailwind CSS:** Utility-first CSS framework for rapid UI development and consistent styling.

## **3. Backend (API & Logic)**
* **Python:** Python serves as our primary backend language, chosen for its excellent AI/ML ecosystem, readability, and extensive library support. Python's simplicity allows for rapid development while maintaining code quality.

* **FastAPI:** FastAPI is our modern, high-speed web framework for building APIs. It provides automatic API documentation, type validation with Pydantic, and exceptional performance that rivals Node.js and Go. FastAPI's async support makes it ideal for handling concurrent requests and AI processing tasks.

* **Uvicorn:** ASGI server that runs our FastAPI application with support for WebSockets and async operations.

* **Key Python Libraries:**
  - **Pydantic:** Provides data validation and serialization using Python type annotations.
  - **MySQL Connector Python:** Official MySQL database driver with connection pooling.
  - **Python-JOSE:** Handles JWT token generation and validation for authentication.
  - **Python-Multipart:** Processes file uploads and form data.
  - **Python-Dotenv:** Manages environment variables and configuration.
  - **Requests:** HTTP client for making external API calls.

## **4. Database**
* **MySQL:** MySQL serves as our primary relational database for securely storing structured data including user information, complaint details, status updates, and metadata. We chose MySQL for its reliability, ACID compliance, excellent performance with large datasets, and strong ecosystem support. The database uses connection pooling for optimal performance and includes proper indexing for efficient querying.

* **Database Schema:**
  - Complaints table with fields for title, description, location, image URLs, PDF URLs, status, and timestamps
  - Connection pooling with 5 concurrent connections for optimal performance
  - Proper indexing on frequently queried fields like status and creation date

## **5. Cloud & External Services**

### **AI Services:**
* **Google Gemini API:** Powers our intelligent image analysis and description generation. When users upload photos of civic issues, Gemini analyzes the image and automatically generates both a descriptive title and detailed problem description, significantly reducing manual data entry and improving accuracy.

* **OpenAI API (Alternative):** Provides backup AI capabilities for image analysis and text generation, ensuring redundancy in our AI processing pipeline.

### **Mapping Services:**
* **OpenStreetMap:** Provides free, open-source map tiles for our interactive maps in the admin dashboard. This service displays complaint locations and allows administrators to visualize the geographic distribution of issues.

* **Google Maps Integration:** Enables users to view complaint locations in Google Maps for navigation and context, providing seamless integration with familiar mapping services.

### **File Storage:**
* **Local File System:** Currently stores uploaded images and generated PDFs locally on the server. The system is designed to be easily migrated to cloud storage solutions like AWS S3 or Google Cloud Storage for production deployment.

### **Development & Testing:**
* **Node.js Test Server:** A lightweight Express.js server used for testing message passing between Flutter and React applications during development.

## **6. Architecture & Deployment**

### **Microservices Architecture:**
Our system follows a microservices pattern with separate services for:
- Flutter mobile application (citizen interface)
- React web dashboard (admin interface)  
- FastAPI backend (core business logic and data management)
- Node.js message service (inter-service communication)

### **API Design:**
- RESTful API design with clear endpoint structure
- Comprehensive error handling and status codes
- CORS configuration for cross-origin requests
- File upload support for images and PDFs
- Real-time status updates and notifications

### **Security:**
- JWT-based authentication (ready for implementation)
- CORS middleware for secure cross-origin requests
- Input validation using Pydantic models
- File type validation for uploads
- Environment variable management for sensitive data

### **Scalability Considerations:**
- Database connection pooling for efficient resource usage
- Stateless API design for horizontal scaling
- Modular architecture allowing independent service scaling
- Designed for cloud deployment with containerization support

## **7. Development Tools & Workflow**

### **Version Control:**
- Git for source code management
- Structured repository with separate folders for each service

### **Build Tools:**
- Vite for React development and building
- Flutter's built-in build system for mobile apps
- Uvicorn for Python backend development

### **Code Quality:**
- TypeScript-style validation with Pydantic
- Flutter's built-in linting and analysis tools
- ESLint and Prettier for React code formatting

This technology stack provides a robust, scalable foundation for our civic engagement platform, enabling efficient development, reliable operation, and future growth while maintaining excellent user experience across all platforms.
