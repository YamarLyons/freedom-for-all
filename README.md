# FreedomForAll

**FreedomForAll** is a fully functional news aggregation platform that consolidates news from multiple reputable sources into one convenient location. This platform emphasizes free speech and transparency, providing users with a neutral space to stay informed on a variety of topics. The project demonstrates robust backend development, efficient database management, and an interactive front-end user experience.

---

## Features

### 1. **Dynamic News Aggregation**
- Integrates **web scraping** and **RSS feeds** to fetch articles from trusted sources in real-time.
- Presents articles in a clean and user-friendly layout categorized by source and recency.

### 2. **Search Functionality**
- Users can perform keyword-based searches for articles.
- Optimized database queries ensure search results are fetched efficiently.

### 3. **Media Bias Representation**
- Includes a visual chart that maps the political bias of news sources, helping users understand perspectives.

### 4. **Content Sections**
- **Twitter Feed:** Live Twitter updates from relevant accounts.
- **YouTube Integration:** Embedded videos to complement news stories.
- **Info Section:** Provides details about the site’s mission to promote transparency and free speech.

### 5. **Mobile Responsiveness**
- Designed to work seamlessly across desktops, tablets, and mobile devices using responsive CSS.

---

## Technologies Used

### **Frontend:**
- **HTML5, CSS3, JavaScript**: Build responsive and interactive user interfaces.

### **Backend:**
- **Flask**: Manages the backend logic and API routes.
- **Python**: Implements scraping and data processing.

### **Database:**
- **PostgreSQL**: Stores and manages articles, ensuring fast retrieval through indexed queries.

### **Hosting:**
- **Render**: Deployed for public access at [FreedomForAll](https://freedomforall.onrender.com).

### **Other Tools:**
- **SQLAlchemy**: Handles database ORM for efficient data operations.
- **Dotenv**: Manages environment variables securely.

---

## Installation and Setup

### 1. **Clone the Repository**
```bash
https://github.com/<your-repo>/freedomforall.git
```

### 2. **Set Up Virtual Environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. **Install Dependencies**
```bash
pip install -r requirements.txt
```

### 4. **Set Environment Variables**
Create a `.env` file in the root directory with the following details:
```env
FLASK_APP=app.py
FLASK_ENV=development
DATABASE_URL=postgresql://<user>:<password>@<host>:<port>/<database>
```

### 5. **Run the Application**
```bash
flask run
```
Visit `http://127.0.0.1:5000` in your browser.

---

## Deployment
The site is hosted on **Render** and can be accessed live at:
[https://freedomforall.onrender.com](https://freedomforall.onrender.com)

---

## Future Enhancements
- Implementing user accounts for personalized news feeds.
- Adding a comment section for articles.
- Expanding the list of integrated news sources.
- Introducing push notifications for breaking news.

---

## Contributing
1. Fork the repository.
2. Create a new branch for your feature (`git checkout -b feature-name`).
3. Commit your changes (`git commit -m 'Add a new feature'`).
4. Push to the branch (`git push origin feature-name`).
5. Open a pull request.

---


