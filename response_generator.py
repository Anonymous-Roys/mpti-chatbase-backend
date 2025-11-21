class ResponseGenerator:
    def __init__(self):
        self.response_templates = {
            'greeting': """👋 Hello! Welcome to MPTI Technical Institute!

I'm your MPTI Assistant. I can help you with:
• 🎓 Programs and Courses
• 📝 TACT Program Information
• 🏫 Admissions Process
• 📞 Contact Information

What would you like to know about MPTI?""",
            
            'tact_program': """🚀 **TACT Program**

Technical Advancement and Certification Training program for professional development.

**Learn More:** https://www.mptigh.com/tact-program
**Apply:** https://www.mptigh.com/admissions""",
            
            'application': """📝 **Ready to Join MPTI Technical Institute?**

**Application Process:**
• Applications accepted year-round
• Various entry requirements by program
• Financial aid available
• Scholarship opportunities

**Next Steps:**
🎯 **Start Application:** https://www.mptigh.com/admissions
📞 **Contact Admissions:** https://www.mptigh.com/contact
📋 **View Programs:** https://www.mptigh.com/programs""",
            
            'programs': """🎓 **MPTI Technical Institute Programs**

**Our Offerings:**
• Technical Education Programs
• Engineering & Technology Courses
• Professional Certification Programs
• TACT Program (Technical Advancement)
• Skills Development Training

**Explore More:**
📋 **All Programs:** https://www.mptigh.com/programs
🚀 **TACT Program:** https://www.mptigh.com/tact-program
📝 **Apply:** https://www.mptigh.com/admissions""",
            
            'contact': """📞 **Get in Touch with MPTI**

**Contact Information:**
🌐 **Website:** https://www.mptigh.com/
📧 **Contact Page:** https://www.mptigh.com/contact

**Quick Actions:**
• 📝 **Apply Now:** https://www.mptigh.com/admissions
• 🎓 **View Programs:** https://www.mptigh.com/programs
• 🏫 **About MPTI:** https://www.mptigh.com/about""",
            
            'history': """🏛️ **MPTI Technical Institute History**

MPTI Technical Institute has been serving the technical education community, establishing itself as a leading institution in technical and engineering education.

**Learn More About Our Journey:**
🏫 **About MPTI:** https://www.mptigh.com/about
🎓 **Programs:** https://www.mptigh.com/programs""",
            
            'general': """🏫 **Welcome to MPTI Technical Institute!**

I'm here to help with MPTI information.

**Quick Links:**
• **Programs:** https://www.mptigh.com/programs
• **TACT Program:** https://www.mptigh.com/tact-program
• **Apply:** https://www.mptigh.com/admissions

What would you like to know?"""
        }
        
        self.cta_templates = {
            'tact_program': [
                {'text': 'Learn More About TACT', 'url': 'https://www.mptigh.com/tact-program'},
                {'text': 'Apply for TACT Program', 'url': 'https://www.mptigh.com/admissions'}
            ],
            'application': [
                {'text': 'Start Application', 'url': 'https://www.mptigh.com/admissions'},
                {'text': 'Contact Admissions', 'url': 'https://www.mptigh.com/contact'}
            ],
            'programs': [
                {'text': 'View All Programs', 'url': 'https://www.mptigh.com/programs'},
                {'text': 'Apply Now', 'url': 'https://www.mptigh.com/admissions'}
            ],
            'contact': [
                {'text': 'Contact Us', 'url': 'https://www.mptigh.com/contact'},
                {'text': 'Visit Campus', 'url': 'https://www.mptigh.com/about'}
            ]
        }
    
    def generate(self, intent, relevant_content=None):
        """Generate response based on intent and content"""
        if intent in self.response_templates:
            response = self.response_templates[intent]
            
            # Enhance with relevant content if available
            if relevant_content and intent in ['tact_program', 'history', 'general']:
                content_preview = relevant_content[0][:500] + "..." if len(relevant_content[0]) > 500 else relevant_content[0]
                response = f"**MPTI Information**\n\n{content_preview}\n\n{response}"
            
            return response
        
        return self.response_templates['general']
    
    def get_ctas(self, intent):
        """Get call-to-action suggestions for intent"""
        return self.cta_templates.get(intent, [
            {'text': 'Explore Programs', 'url': 'https://www.mptigh.com/programs'},
            {'text': 'Apply Now', 'url': 'https://www.mptigh.com/admissions'}
        ])