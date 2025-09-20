// Resume Relevance Check System - JavaScript
document.addEventListener('DOMContentLoaded', function() {
    initializeFileUpload();
    initializeFormHandling();
    initializeAnimations();
});

// File Upload Functionality
function initializeFileUpload() {
    const fileInput = document.getElementById('resumes');
    const uploadArea = document.getElementById('fileUploadArea');
    const fileList = document.getElementById('fileList');
    
    if (!fileInput || !uploadArea) return;

    let selectedFiles = [];

    // Drag and drop functionality
    uploadArea.addEventListener('dragover', function(e) {
        e.preventDefault();
        uploadArea.classList.add('dragover');
    });

    uploadArea.addEventListener('dragleave', function(e) {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
    });

    uploadArea.addEventListener('drop', function(e) {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
        
        const files = Array.from(e.dataTransfer.files);
        handleFileSelection(files);
    });

    // File input change
    fileInput.addEventListener('change', function(e) {
        const files = Array.from(e.target.files);
        handleFileSelection(files);
    });

    // Handle file selection
    function handleFileSelection(files) {
        const allowedExtensions = ['pdf', 'docx', 'txt'];
        const maxFileSize = 16 * 1024 * 1024; // 16MB
        
        files.forEach(file => {
            const extension = file.name.split('.').pop().toLowerCase();
            
            if (!allowedExtensions.includes(extension)) {
                showAlert(`File "${file.name}" has unsupported format. Please use PDF, DOCX, or TXT files.`, 'error');
                return;
            }
            
            if (file.size > maxFileSize) {
                showAlert(`File "${file.name}" is too large. Maximum size is 16MB.`, 'error');
                return;
            }
            
            // Check if file already selected
            if (selectedFiles.some(f => f.name === file.name && f.size === file.size)) {
                showAlert(`File "${file.name}" is already selected.`, 'error');
                return;
            }
            
            selectedFiles.push(file);
        });
        
        updateFileList();
        updateFileInput();
    }

    // Update file list display
    function updateFileList() {
        if (!fileList) return;
        
        fileList.innerHTML = '';
        
        if (selectedFiles.length === 0) {
            fileList.style.display = 'none';
            return;
        }
        
        fileList.style.display = 'block';
        
        selectedFiles.forEach((file, index) => {
            const fileItem = document.createElement('div');
            fileItem.className = 'file-item';
            
            const fileInfo = document.createElement('div');
            fileInfo.className = 'file-info';
            
            const fileIcon = document.createElement('span');
            fileIcon.className = 'file-icon';
            fileIcon.textContent = getFileIcon(file.name);
            
            const fileName = document.createElement('span');
            fileName.className = 'file-name';
            fileName.textContent = file.name;
            
            const fileSize = document.createElement('span');
            fileSize.className = 'file-size';
            fileSize.textContent = formatFileSize(file.size);
            
            const removeBtn = document.createElement('button');
            removeBtn.className = 'remove-file';
            removeBtn.textContent = 'Remove';
            removeBtn.type = 'button';
            removeBtn.onclick = () => removeFile(index);
            
            fileInfo.appendChild(fileIcon);
            fileInfo.appendChild(fileName);
            fileInfo.appendChild(fileSize);
            
            fileItem.appendChild(fileInfo);
            fileItem.appendChild(removeBtn);
            
            fileList.appendChild(fileItem);
        });
    }

    // Remove file from selection
    function removeFile(index) {
        selectedFiles.splice(index, 1);
        updateFileList();
        updateFileInput();
    }

    // Update the actual file input
    function updateFileInput() {
        if (!fileInput) return;
        
        const dt = new DataTransfer();
        selectedFiles.forEach(file => dt.items.add(file));
        fileInput.files = dt.files;
    }

    // Get file icon based on extension
    function getFileIcon(filename) {
        const extension = filename.split('.').pop().toLowerCase();
        switch(extension) {
            case 'pdf': return '📄';
            case 'docx': return '📝';
            case 'txt': return '📋';
            default: return '📄';
        }
    }

    // Format file size
    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
}

// Form Handling
function initializeFormHandling() {
    const form = document.getElementById('uploadForm');
    const submitBtn = document.getElementById('submitBtn');
    const submitText = document.getElementById('submitText');
    const loadingSpinner = document.getElementById('loadingSpinner');
    
    if (!form) return;

    form.addEventListener('submit', function(e) {
        if (!validateForm()) {
            e.preventDefault();
            return;
        }
        
        // Show loading state
        if (submitBtn && submitText && loadingSpinner) {
            submitBtn.disabled = true;
            submitText.style.display = 'none';
            loadingSpinner.style.display = 'inline-block';
            submitBtn.style.cursor = 'not-allowed';
        }
        
        // Show progress message
        showAlert('Processing resumes... This may take a few moments.', 'info');
    });

    // Form validation
    function validateForm() {
        const jobDescription = document.getElementById('job_description');
        const resumesInput = document.getElementById('resumes');
        
        if (!jobDescription || !jobDescription.value.trim()) {
            showAlert('Please provide a job description.', 'error');
            if (jobDescription) jobDescription.focus();
            return false;
        }
        
        if (jobDescription.value.trim().length < 50) {
            showAlert('Job description seems too short. Please provide more details for better matching.', 'error');
            jobDescription.focus();
            return false;
        }
        
        if (!resumesInput || resumesInput.files.length === 0) {
            showAlert('Please upload at least one resume file.', 'error');
            return false;
        }
        
        return true;
    }
}

// Animations and Visual Effects
function initializeAnimations() {
    // Animate elements on scroll
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);

    // Observe elements for animation
    const animatedElements = document.querySelectorAll('.instruction-item, .feature-item');
    animatedElements.forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(20px)';
        el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(el);
    });

    // Add hover effects to cards
    const cards = document.querySelectorAll('.instruction-item, .feature-item');
    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px) scale(1.02)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
        });
    });
}

// Utility Functions
function showAlert(message, type = 'info') {
    // Remove existing alerts
    const existingAlerts = document.querySelectorAll('.dynamic-alert');
    existingAlerts.forEach(alert => alert.remove());
    
    // Create new alert
    const alert = document.createElement('div');
    alert.className = `alert alert-${type} dynamic-alert`;
    alert.innerHTML = `
        ${message}
        <button type="button" class="close" onclick="this.parentElement.remove()">&times;</button>
    `;
    
    // Insert at top of container
    const container = document.querySelector('.container');
    if (container) {
        container.insertBefore(alert, container.firstChild);
        
        // Auto remove after 5 seconds for info messages
        if (type === 'info') {
            setTimeout(() => {
                if (alert.parentNode) {
                    alert.remove();
                }
            }, 5000);
        }
    }
}

// Character counter for textarea
function initializeCharacterCounter() {
    const textarea = document.getElementById('job_description');
    if (!textarea) return;
    
    const counter = document.createElement('div');
    counter.className = 'character-counter';
    counter.style.cssText = 'text-align: right; margin-top: 5px; color: #6c757d; font-size: 0.85rem;';
    
    textarea.parentNode.appendChild(counter);
    
    function updateCounter() {
        const count = textarea.value.length;
        counter.textContent = `${count} characters`;
        
        if (count < 50) {
            counter.style.color = '#dc3545';
        } else if (count < 100) {
            counter.style.color = '#fd7e14';
        } else {
            counter.style.color = '#28a745';
        }
    }
    
    textarea.addEventListener('input', updateCounter);
    updateCounter();
}

// Initialize character counter when DOM is loaded
document.addEventListener('DOMContentLoaded', initializeCharacterCounter);

// Auto-resize textarea
function initializeAutoResize() {
    const textarea = document.getElementById('job_description');
    if (!textarea) return;
    
    function autoResize() {
        this.style.height = 'auto';
        this.style.height = (this.scrollHeight) + 'px';
    }
    
    textarea.addEventListener('input', autoResize);
    textarea.addEventListener('paste', () => setTimeout(autoResize, 0));
}

// Initialize auto-resize when DOM is loaded
document.addEventListener('DOMContentLoaded', initializeAutoResize);

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Ctrl+Enter to submit form
    if (e.ctrlKey && e.key === 'Enter') {
        const form = document.getElementById('uploadForm');
        if (form) {
            form.dispatchEvent(new Event('submit', { cancelable: true }));
        }
    }
    
    // Escape to clear form
    if (e.key === 'Escape') {
        const jobDescription = document.getElementById('job_description');
        const confirmClear = confirm('Clear the form?');
        if (confirmClear && jobDescription) {
            jobDescription.value = '';
            const fileInput = document.getElementById('resumes');
            if (fileInput) {
                fileInput.value = '';
                const fileList = document.getElementById('fileList');
                if (fileList) {
                    fileList.innerHTML = '';
                    fileList.style.display = 'none';
                }
            }
        }
    }
});

// Progress indication for file processing
function showProcessingProgress(files) {
    const progressContainer = document.createElement('div');
    progressContainer.className = 'processing-progress';
    progressContainer.innerHTML = `
        <div style="background: #f8f9fa; padding: 20px; border-radius: 10px; margin: 20px 0; text-align: center;">
            <h4 style="color: #2c3e50; margin-bottom: 15px;">Processing ${files.length} resume(s)...</h4>
            <div style="background: #e9ecef; height: 8px; border-radius: 4px; overflow: hidden;">
                <div class="progress-bar" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); height: 100%; width: 0%; transition: width 0.3s ease;"></div>
            </div>
            <p style="color: #6c757d; margin-top: 10px; font-size: 0.9rem;">Please wait while we analyze the resumes...</p>
        </div>
    `;
    
    const container = document.querySelector('.upload-section');
    if (container) {
        container.appendChild(progressContainer);
        
        // Simulate progress
        const progressBar = progressContainer.querySelector('.progress-bar');
        let progress = 0;
        const interval = setInterval(() => {
            progress += Math.random() * 15;
            if (progress > 90) progress = 90;
            progressBar.style.width = progress + '%';
        }, 500);
        
        // Clean up interval when form submits
        const form = document.getElementById('uploadForm');
        if (form) {
            form.addEventListener('submit', () => {
                clearInterval(interval);
                progressBar.style.width = '100%';
            });
        }
    }
}

// Sample job descriptions for quick testing
const sampleJobDescriptions = {
    'software-developer': `We are seeking a talented Software Developer to join our dynamic team.

Requirements:
- 3+ years of experience in software development
- Proficiency in Python, JavaScript, and SQL
- Experience with React, Django, or similar frameworks
- Strong problem-solving and analytical skills
- Bachelor's degree in Computer Science or related field
- Experience with version control systems (Git)
- Knowledge of database systems (MySQL, PostgreSQL)
- Familiarity with cloud platforms (AWS, Azure) preferred

Responsibilities:
- Develop and maintain web applications
- Collaborate with cross-functional teams
- Write clean, maintainable code
- Participate in code reviews
- Debug and resolve technical issues`,

    'data-scientist': `Looking for an experienced Data Scientist to drive data-driven decision making.

Requirements:
- Master's degree in Data Science, Statistics, or related field
- 4+ years of experience in data analysis and machine learning
- Proficiency in Python, R, and SQL
- Experience with pandas, numpy, scikit-learn, TensorFlow
- Strong statistical analysis and modeling skills
- Experience with data visualization tools (matplotlib, seaborn, Plotly)
- Knowledge of big data technologies (Spark, Hadoop) preferred
- Excellent communication and presentation skills

Responsibilities:
- Build and deploy machine learning models
- Analyze large datasets to extract insights
- Create data visualizations and reports
- Collaborate with business stakeholders`,

    'marketing-manager': `Seeking a dynamic Marketing Manager to lead our marketing initiatives.

Requirements:
- Bachelor's degree in Marketing, Business, or related field
- 5+ years of marketing experience
- Strong analytical and strategic thinking skills
- Experience with digital marketing campaigns
- Proficiency in Google Analytics, Facebook Ads, Google Ads
- Excellent written and verbal communication
- Experience with CRM systems
- Knowledge of SEO/SEM best practices
- Leadership and team management experience

Responsibilities:
- Develop and execute marketing strategies
- Manage digital marketing campaigns
- Analyze marketing performance metrics
- Lead marketing team and collaborate across departments`
};

// Add sample job description functionality
function initializeSampleDescriptions() {
    const textarea = document.getElementById('job_description');
    if (!textarea) return;
    
    // Create sample selector
    const sampleContainer = document.createElement('div');
    sampleContainer.className = 'sample-descriptions';
    sampleContainer.innerHTML = `
        <div style="margin-bottom: 10px;">
            <small style="color: #6c757d;">Quick start with sample job descriptions:</small>
        </div>
        <div style="display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 15px;">
            <button type="button" class="btn-sample" data-sample="software-developer">Software Developer</button>
            <button type="button" class="btn-sample" data-sample="data-scientist">Data Scientist</button>
            <button type="button" class="btn-sample" data-sample="marketing-manager">Marketing Manager</button>
        </div>
    `;
    
    // Insert before textarea
    textarea.parentNode.insertBefore(sampleContainer, textarea);
    
    // Add styles for sample buttons
    const style = document.createElement('style');
    style.textContent = `
        .btn-sample {
            background: #6c757d;
            color: white;
            border: none;
            padding: 6px 12px;
            border-radius: 4px;
            font-size: 0.8rem;
            cursor: pointer;
            transition: background 0.3s ease;
        }
        .btn-sample:hover {
            background: #5a6268;
        }
    `;
    document.head.appendChild(style);
    
    // Add click handlers
    const sampleButtons = sampleContainer.querySelectorAll('.btn-sample');
    sampleButtons.forEach(button => {
        button.addEventListener('click', function() {
            const sampleType = this.dataset.sample;
            const sampleText = sampleJobDescriptions[sampleType];
            if (sampleText) {
                textarea.value = sampleText;
                textarea.dispatchEvent(new Event('input')); // Trigger counter update
                showAlert('Sample job description loaded! You can modify it as needed.', 'info');
            }
        });
    });
}

// Initialize sample descriptions when DOM is loaded
document.addEventListener('DOMContentLoaded', initializeSampleDescriptions);

// Local storage for form persistence
function initializeFormPersistence() {
    const textarea = document.getElementById('job_description');
    if (!textarea) return;
    
    const storageKey = 'resume_checker_job_description';
    
    // Load saved content
    const savedContent = localStorage.getItem(storageKey);
    if (savedContent && !textarea.value) {
        textarea.value = savedContent;
        textarea.dispatchEvent(new Event('input'));
    }
    
    // Save content on input
    let saveTimeout;
    textarea.addEventListener('input', function() {
        clearTimeout(saveTimeout);
        saveTimeout = setTimeout(() => {
            localStorage.setItem(storageKey, this.value);
        }, 1000); // Save after 1 second of inactivity
    });
    
    // Clear storage on successful form submission
    const form = document.getElementById('uploadForm');
    if (form) {
        form.addEventListener('submit', function() {
            localStorage.removeItem(storageKey);
        });
    }
}

// Initialize form persistence when DOM is loaded
document.addEventListener('DOMContentLoaded', initializeFormPersistence);

// File preview functionality
function initializeFilePreview() {
    const fileInput = document.getElementById('resumes');
    if (!fileInput) return;
    
    fileInput.addEventListener('change', function() {
        const files = Array.from(this.files);
        files.forEach((file, index) => {
            if (file.type === 'text/plain' && file.size < 50000) { // Only preview small text files
                const reader = new FileReader();
                reader.onload = function(e) {
                    console.log(`Preview of ${file.name}:`, e.target.result.substring(0, 200) + '...');
                };
                reader.readAsText(file);
            }
        });
    });
}

// Initialize file preview when DOM is loaded
document.addEventListener('DOMContentLoaded', initializeFilePreview);

// Accessibility improvements
function initializeAccessibility() {
    // Add ARIA labels
    const fileUploadArea = document.getElementById('fileUploadArea');
    if (fileUploadArea) {
        fileUploadArea.setAttribute('role', 'button');
        fileUploadArea.setAttribute('aria-label', 'Click to select resume files or drag and drop files here');
        fileUploadArea.setAttribute('tabindex', '0');
        
        // Keyboard navigation for file upload
        fileUploadArea.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                document.getElementById('resumes').click();
            }
        });
    }
    
    // Add focus indicators
    const focusableElements = document.querySelectorAll('input, textarea, button, [tabindex]:not([tabindex="-1"])');
    focusableElements.forEach(element => {
        element.addEventListener('focus', function() {
            this.style.outline = '2px solid #667eea';
            this.style.outlineOffset = '2px';
        });
        
        element.addEventListener('blur', function() {
            this.style.outline = '';
            this.style.outlineOffset = '';
        });
    });
}

// Initialize accessibility when DOM is loaded
document.addEventListener('DOMContentLoaded', initializeAccessibility);

// Error handling and user feedback
function handleErrors() {
    window.addEventListener('error', function(e) {
        console.error('JavaScript error:', e.error);
        showAlert('An unexpected error occurred. Please refresh the page and try again.', 'error');
    });
    
    window.addEventListener('unhandledrejection', function(e) {
        console.error('Unhandled promise rejection:', e.reason);
        showAlert('A network error occurred. Please check your connection and try again.', 'error');
    });
}

// Initialize error handling when DOM is loaded
document.addEventListener('DOMContentLoaded', handleErrors);

// Performance monitoring
function initializePerformanceMonitoring() {
    if ('performance' in window) {
        window.addEventListener('load', function() {
            setTimeout(function() {
                const perfData = performance.getEntriesByType('navigation')[0];
                const loadTime = perfData.loadEventEnd - perfData.loadEventStart;
                console.log(`Page load time: ${loadTime}ms`);
                
                // Show warning if page loads slowly
                if (loadTime > 3000) {
                    console.warn('Page loaded slowly. Consider optimizing resources.');
                }
            }, 0);
        });
    }
}

// Initialize performance monitoring when DOM is loaded
document.addEventListener('DOMContentLoaded', initializePerformanceMonitoring);

// Mobile-specific enhancements
function initializeMobileEnhancements() {
    const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
    
    if (isMobile) {
        // Adjust file upload area for mobile
        const uploadArea = document.getElementById('fileUploadArea');
        if (uploadArea) {
            uploadArea.style.padding = '30px 15px';
        }
        
        // Add mobile-specific styles
        const mobileStyle = document.createElement('style');
        mobileStyle.textContent = `
            @media (max-width: 768px) {
                .file-item {
                    flex-direction: column;
                    gap: 10px;
                }
                .file-info {
                    justify-content: center;
                    text-align: center;
                }
                .remove-file {
                    align-self: center;
                    width: 100px;
                }
            }
        `;
        document.head.appendChild(mobileStyle);
        
        // Prevent zoom on input focus for iOS
        const inputs = document.querySelectorAll('input, textarea');
        inputs.forEach(input => {
            input.addEventListener('focus', function() {
                const viewport = document.querySelector('meta[name=viewport]');
                if (viewport) {
                    const originalContent = viewport.content;
                    viewport.content = 'width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=0';
                    
                    this.addEventListener('blur', function() {
                        viewport.content = originalContent;
                    }, { once: true });
                }
            });
        });
    }
}

// Initialize mobile enhancements when DOM is loaded
document.addEventListener('DOMContentLoaded', initializeMobileEnhancements);

// Theme toggle (for future dark mode support)
function initializeThemeToggle() {
    // This is a placeholder for future theme functionality
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)');
    
    prefersDark.addEventListener('change', function(e) {
        if (e.matches) {
            console.log('User prefers dark mode');
            // Future: Apply dark theme
        } else {
            console.log('User prefers light mode');
            // Future: Apply light theme
        }
    });
}

// Initialize theme toggle when DOM is loaded
document.addEventListener('DOMContentLoaded', initializeThemeToggle);

// Utility function to debounce events
function debounce(func, wait, immediate) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            timeout = null;
            if (!immediate) func.apply(this, args);
        };
        const callNow = immediate && !timeout;
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
        if (callNow) func.apply(this, args);
    };
}

// Utility function to throttle events
function throttle(func, limit) {
    let inThrottle;
    return function executedFunction(...args) {
        if (!inThrottle) {
            func.apply(this, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// Export functions for potential use by other scripts
window.ResumeChecker = {
    showAlert,
    debounce,
    throttle,
    initializeFileUpload,
    initializeFormHandling,
    initializeAnimations
};

console.log('Resume Relevance Check System JavaScript loaded successfully!');