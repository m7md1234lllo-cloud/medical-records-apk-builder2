// Voice Input Module using Web Speech API
// دعم الإدخال الصوتي باللغة العربية والإنجليزية

const VoiceInput = {
    recognition: null,
    isListening: false,
    currentButton: null,
    currentTarget: null,
    currentLanguage: 'ar-SA', // Default to Arabic

    init() {
        // Check if browser supports Speech Recognition
        if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
            console.warn('Speech Recognition not supported');
            return;
        }

        // Initialize Speech Recognition
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        this.recognition = new SpeechRecognition();
        
        // Configure recognition - Start with Arabic but accept both
        this.recognition.lang = this.currentLanguage;
        this.recognition.continuous = false;
        this.recognition.interimResults = false;
        this.recognition.maxAlternatives = 5; // Get more alternatives to find best match

        // Event listeners
        this.recognition.onstart = () => {
            this.isListening = true;
            if (this.currentButton) {
                this.currentButton.classList.add('listening');
                this.currentButton.textContent = '🔴';
            }
            console.log('Speech recognition started, language:', this.recognition.lang);
        };

        this.recognition.onresult = (event) => {
            // Try to get the best result from all alternatives
            let transcript = event.results[0][0].transcript;
            let confidence = event.results[0][0].confidence;
            
            console.log('Recognition result:', transcript, 'Confidence:', confidence);
            
            // Try other alternatives if available
            for (let i = 1; i < event.results[0].length; i++) {
                const alternative = event.results[0][i].transcript;
                const altConfidence = event.results[0][i].confidence;
                console.log('Alternative ' + i + ':', alternative, 'Confidence:', altConfidence);
                
                // If alternative has better confidence, use it
                if (altConfidence > confidence) {
                    transcript = alternative;
                    confidence = altConfidence;
                }
            }
            
            if (this.currentTarget) {
                const element = document.getElementById(this.currentTarget);
                if (element) {
                    // Process the transcript
                    let processedText = this.processTranscript(transcript);
                    
                    if (element.tagName === 'INPUT' || element.tagName === 'TEXTAREA') {
                        if (element.type === 'number' || element.type === 'tel') {
                            // For number/phone inputs, extract and clean numbers
                            const cleaned = processedText.replace(/\s+/g, '');
                            const numbers = cleaned.match(/\d+\.?\d*/);
                            if (numbers) {
                                element.value = numbers[0];
                                element.dispatchEvent(new Event('input'));
                            }
                        } else {
                            // For text inputs, keep the text as-is (supports Arabic and English)
                            // Just trim extra spaces
                            processedText = processedText.trim();
                            
                            if (element.value) {
                                element.value += '\n' + processedText;
                            } else {
                                element.value = processedText;
                            }
                            element.dispatchEvent(new Event('input'));
                        }
                    }
                }
            }
        };

        this.recognition.onerror = (event) => {
            console.error('Speech recognition error:', event.error);
            
            // If no speech detected in Arabic, try English automatically
            if (event.error === 'no-speech' && this.currentLanguage === 'ar-SA') {
                console.log('No speech in Arabic, trying English...');
                this.currentLanguage = 'en-US';
                this.recognition.lang = 'en-US';
                
                // Restart with English
                setTimeout(() => {
                    if (this.currentButton && this.currentTarget) {
                        this.startListening();
                    }
                }, 500);
                return;
            }
            
            this.stopListening();
            
            if (event.error === 'no-speech') {
                alert('⚠️ لم يتم اكتشاف صوت.\n\nحاول مرة أخرى وتحدث بوضوح.\n(يدعم العربية والإنجليزية)');
            } else if (event.error === 'not-allowed') {
                alert('❌ يرجى السماح بالوصول إلى الميكروفون من إعدادات المتصفح.');
            } else if (event.error === 'aborted') {
                // Silently handle abort (usually means user stopped)
                console.log('Recognition aborted');
            } else {
                console.log('Recognition error:', event.error);
            }
        };

        this.recognition.onend = () => {
            this.stopListening();
            // Reset to Arabic for next time
            this.currentLanguage = 'ar-SA';
            this.recognition.lang = 'ar-SA';
        };

        // Attach to all voice buttons
        this.attachToButtons();
    },

    attachToButtons() {
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('voice-btn')) {
                e.preventDefault();
                const target = e.target.getAttribute('data-target');
                if (target) {
                    this.toggleListening(e.target, target);
                }
            }
        });
    },

    toggleListening(button, target) {
        if (this.isListening) {
            this.recognition.stop();
        } else {
            this.currentButton = button;
            this.currentTarget = target;
            this.startListening();
        }
    },

    startListening() {
        try {
            this.recognition.start();
        } catch (error) {
            console.error('Error starting recognition:', error);
        }
    },

    stopListening() {
        this.isListening = false;
        if (this.currentButton) {
            this.currentButton.classList.remove('listening');
            this.currentButton.textContent = '🎤';
            this.currentButton = null;
        }
        this.currentTarget = null;
    },

    processTranscript(text) {
        console.log('Original transcript:', text);
        
        // First, check if this is mainly numbers (phone number or ID)
        const digitsOnly = text.replace(/\D/g, '');
        const hasNumbers = digitsOnly.length > 0;
        
        if (hasNumbers && digitsOnly.length > 3) {
            // This looks like a phone number or ID - remove ALL spaces
            text = text.replace(/\s+/g, '');
            console.log('Processed as number:', text);
            return text;
        }
        
        // Remove spaces between individual digits (0 9 6 5 → 0965)
        text = text.replace(/(\d)\s+(\d)/g, '$1$2');
        
        // Convert Arabic number words to digits
        const arabicNumbers = {
            'صفر': '0', 'واحد': '1', 'اثنان': '2', 'اثنين': '2',
            'ثلاثة': '3', 'أربعة': '4', 'خمسة': '5',
            'ستة': '6', 'سبعة': '7', 'ثمانية': '8',
            'تسعة': '9', 'عشرة': '10', 'عشرين': '20',
            'ثلاثين': '30', 'أربعين': '40', 'خمسين': '50',
            'ستين': '60', 'سبعين': '70', 'ثمانين': '80',
            'تسعين': '90', 'مائة': '100', 'مئة': '100',
            'ألف': '1000'
        };

        for (let word in arabicNumbers) {
            text = text.replace(new RegExp(word, 'g'), arabicNumbers[word]);
        }
        
        console.log('Final processed text:', text);
        return text;
    }
};

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => VoiceInput.init());
} else {
    VoiceInput.init();
}

// Export for use in other modules
window.VoiceInput = VoiceInput;
