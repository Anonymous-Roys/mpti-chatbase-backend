import random
import logging
from datetime import datetime
from ai_service import AIService

logger = logging.getLogger(__name__)

class AdvancedResponseGenerator:
    def __init__(self):
        self.ai_service = AIService()
        self.response_templates = {
            'greeting': {
                'positive': "Hello! Great to hear from you! 👋 Welcome to MPTI Technical Institute!",
                'neutral': "👋 Hello! Welcome to MPTI Technical Institute!",
                'negative': "Hello! I'm here to help make your MPTI experience better. 👋"
            },
            'programs': {
                'comparison': "Here's a comparison of our programs to help you decide:",
                'detailed': "Let me provide detailed information about our programs:",
                'general': "🎓 **MPTI Technical Institute Programs**"
            },
            'application': {
                'urgent': "I understand you need application information quickly! Here's what you need:",
                'detailed': "Let me walk you through the complete application process:",
                'general': "📝 **Ready to Join MPTI Technical Institute?**"
            }
        }
        
        self.dynamic_content = {
            'programs': [
                "• **Mechanical Engineering Technology** - Hands-on training with industry equipment",
                "• **Electrical Engineering Technology** - Power systems and control technology",
                "• **Welding and Fabrication** - Advanced welding techniques and certification",
                "• **Instrumentation and Control** - Process control and automation systems"
            ],
            'benefits': [
                "✅ Industry-standard equipment and facilities",
                "✅ Experienced instructors with industry background",
                "✅ Job placement assistance after graduation",
                "✅ Flexible scheduling options available"
            ],
            'application_steps': [
                "1. **Complete Application Form** - Available online or in-person",
                "2. **Submit Required Documents** - Transcripts and identification",
                "3. **Schedule Interview** - Meet with our admissions team",
                "4. **Financial Planning** - Discuss payment options and aid"
            ]
        }
    
    def generate_contextual_response(self, intent, nlp_analysis, relevant_content=None, conversation_context=None):
        """Generate AI-powered contextual response"""
        
        # Build context for AI
        context_parts = []
        if relevant_content:
            context_parts.append(f"Website Content: {relevant_content[0][:300]}")
        if conversation_context:
            recent_topics = conversation_context.get('recent_intents', [])
            if recent_topics:
                context_parts.append(f"Recent topics: {', '.join(recent_topics[-3:])}")
        
        context = " | ".join(context_parts)
        
        # Get AI-generated response
        message = nlp_analysis.get('original_message', '')
        ai_response = self.ai_service.generate_response(message, context, intent)
        
        # Add smart CTAs
        cta_content = self._generate_smart_cta(intent, nlp_analysis, conversation_context)
        
        return f"{ai_response}\n\n{cta_content}"
    
    def _determine_response_style(self, nlp_analysis, conversation_context):
        """Determine appropriate response style"""
        signals = nlp_analysis.get('intent_signals', {})
        sentiment = nlp_analysis.get('sentiment', 'neutral')
        
        if signals.get('urgency'):
            return 'urgent'
        elif signals.get('wants_details') or nlp_analysis.get('length', 0) > 10:
            return 'detailed'
        elif signals.get('comparison'):
            return 'comparison'
        elif sentiment == 'negative':
            return 'negative'
        elif sentiment == 'positive':
            return 'positive'
        else:
            return 'general'
    
    def _get_template(self, intent, style):
        """Get response template based on intent and style"""
        templates = self.response_templates.get(intent, {})
        
        if style in templates:
            return templates[style]
        elif 'general' in templates:
            return templates['general']
        else:
            return f"Thank you for your question about {intent}."
    
    def _generate_entity_content(self, entities, intent):
        """Generate content based on extracted entities"""
        content_parts = []
        
        if 'programs' in entities:
            programs = entities['programs']
            if 'tact' in programs:
                content_parts.append("🚀 **TACT Program** - Our flagship professional development program")
            if 'mechanical' in programs:
                content_parts.append("⚙️ **Mechanical Engineering** - Comprehensive mechanical systems training")
            if 'electrical' in programs:
                content_parts.append("⚡ **Electrical Engineering** - Power systems and electrical technology")
        
        if 'time_periods' in entities:
            time_info = entities['time_periods']
            if any(period in time_info for period in ['semester', 'year']):
                content_parts.append("📅 **Academic Calendar** - Programs run on semester basis with flexible start dates")
        
        return '\n'.join(content_parts) if content_parts else None
    
    def _generate_question_response(self, question_type, intent):
        """Generate response based on question type"""
        question_responses = {
            'what': {
                'programs': "Our programs include technical education, engineering technology, and professional certifications.",
                'application': "The application process involves completing forms, submitting documents, and meeting requirements."
            },
            'how': {
                'programs': "You can explore programs through our website, campus visits, or speaking with advisors.",
                'application': "Apply online through our admissions portal or visit our campus for in-person assistance."
            },
            'when': {
                'programs': "Programs start multiple times per year with flexible scheduling options.",
                'application': "Applications are accepted year-round with rolling admissions."
            },
            'where': {
                'programs': "Classes are held at our modern campus facilities in Ghana.",
                'contact': "Visit us at our main campus or contact us through our website."
            }
        }
        
        return question_responses.get(question_type, {}).get(intent)
    
    def _get_dynamic_content(self, intent, nlp_analysis):
        """Get dynamic content based on intent and analysis"""
        if intent == 'programs':
            content = "\n**Our Programs:**\n" + '\n'.join(self.dynamic_content['programs'])
            
            # Add benefits if user wants details
            if nlp_analysis.get('intent_signals', {}).get('wants_details'):
                content += "\n\n**Why Choose MPTI:**\n" + '\n'.join(self.dynamic_content['benefits'])
            
            return content
        
        elif intent == 'application':
            return "\n**Application Process:**\n" + '\n'.join(self.dynamic_content['application_steps'])
        
        return None
    
    def _generate_smart_cta(self, intent, nlp_analysis, conversation_context):
        """Generate smart call-to-action based on context"""
        signals = nlp_analysis.get('intent_signals', {})
        
        base_ctas = {
            'programs': [
                "🔗 **Explore Programs:** https://www.mptigh.com/programs",
                "📞 **Speak with Advisor:** https://www.mptigh.com/contact"
            ],
            'application': [
                "📝 **Start Application:** https://www.mptigh.com/admissions",
                "💬 **Chat with Admissions:** https://www.mptigh.com/contact"
            ],
            'tact_program': [
                "🚀 **TACT Program Details:** https://www.mptigh.com/tact-program",
                "📋 **Apply for TACT:** https://www.mptigh.com/admissions"
            ]
        }
        
        ctas = base_ctas.get(intent, [
            "🌐 **Visit Website:** https://www.mptigh.com/",
            "📞 **Contact Us:** https://www.mptigh.com/contact"
        ])
        
        # Add urgency if detected
        if signals.get('urgency'):
            ctas.insert(0, "⚡ **Immediate Assistance:** Call our admissions hotline")
        
        # Add comparison tools if comparison intent detected
        if signals.get('comparison'):
            ctas.append("📊 **Compare Programs:** Use our program comparison tool")
        
        return "\n**Next Steps:**\n" + '\n'.join(f"• {cta}" for cta in ctas[:3])
    
    def generate_follow_up_questions(self, intent, nlp_analysis):
        """Generate intelligent follow-up questions"""
        follow_ups = {
            'programs': [
                "Would you like to know about specific program requirements?",
                "Are you interested in full-time or part-time study options?",
                "Do you have a particular engineering specialization in mind?"
            ],
            'application': [
                "Do you have questions about application requirements?",
                "Would you like information about financial aid options?",
                "Are you ready to schedule a campus visit?"
            ],
            'tact_program': [
                "Are you currently working in a technical field?",
                "Would you like to know about TACT program scheduling?",
                "Do you need information about TACT certification requirements?"
            ]
        }
        
        questions = follow_ups.get(intent, [])
        
        # Filter based on NLP analysis
        if nlp_analysis.get('intent_signals', {}).get('wants_details'):
            # User wants details, ask more specific questions
            return questions[:2]
        
        return questions[:1] if questions else []