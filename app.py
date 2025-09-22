import os
import re
from flask import Flask, render_template, request, jsonify
from groq import Groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Initialize Groq client
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

class BookReviewGenerator:
    def __init__(self):
        self.client = client
    
    def generate_review(self, book_name):
        """Generate a comprehensive book review using Groq API"""
        try:
            prompt = f"""
            Please provide a comprehensive review of the book "{book_name}". Include:
            
            1. **Book Overview**: Brief description of the book and its main theme
            2. **Author Background**: Brief information about the author
            3. **Key Points**: 3-4 main takeaways or plot points
            4. **Writing Style**: Analysis of the author's writing approach
            5. **Target Audience**: Who would benefit from reading this book
            6. **Rating**: Overall rating out of 5 stars with justification
            7. **Final Recommendation**: Whether you'd recommend it and why
            
            Format the response in a clear, engaging manner. If the book doesn't exist or you're unsure, mention that and provide a general literary analysis framework instead.
            """
            
            # Using Llama model available on Groq
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                model="llama-3.3-70b-versatile",  # Free model on Groq
                temperature=0.7,
                max_tokens=1500
            )
            
            return chat_completion.choices[0].message.content
            
        except Exception as e:
            return f"Error generating review: {str(e)}"
    
    def categorize_book(self, book_name):
        """Determine if book is Fiction or Non-Fiction"""
        try:
            prompt = f"""
            Analyze the book "{book_name}" and determine if it's:
            1. Fiction
            2. Non-Fiction
            3. Unknown/Uncertain
            
            Respond with only one word: "Fiction", "Non-Fiction", or "Unknown"
            """
            
            chat_completion = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.1-8b-instant",  # Faster model for simple categorization
                temperature=0.3,
                max_tokens=10
            )
            
            category = chat_completion.choices[0].message.content.strip()
            return category if category in ["Fiction", "Non-Fiction", "Unknown"] else "Unknown"
            
        except Exception as e:
            return "Unknown"

# Initialize the review generator
review_generator = BookReviewGenerator()

@app.route('/')
def home():
    """Homepage with book search form"""
    return render_template('index.html')

@app.route('/generate_review', methods=['POST'])
def generate_review():
    """API endpoint to generate book review"""
    try:
        data = request.get_json()
        book_name = data.get('book_name', '').strip()
        
        if not book_name:
            return jsonify({'error': 'Please enter a book name'}), 400
        
        # Generate category and review
        category = review_generator.categorize_book(book_name)
        review = review_generator.generate_review(book_name)
        
        return jsonify({
            'book_name': book_name,
            'category': category,
            'review': review,
            'success': True
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/review/<path:book_name>')
def show_review(book_name):
    """Display review page for a specific book"""
    return render_template('review.html', book_name=book_name)

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'BookScan API'})

# FIXED: Changed port from 5000 to 8000 to avoid macOS AirPlay Receiver conflict
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
