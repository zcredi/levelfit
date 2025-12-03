// Mobile Menu Toggle
const menuToggle = document.querySelector('.menu-toggle');
const navMenu = document.querySelector('.nav-menu-left');

if (menuToggle && navMenu) {
    menuToggle.addEventListener('click', () => {
        navMenu.classList.toggle('active');
    });
}

// Close mobile menu when clicking on a link
document.querySelectorAll('.nav-menu a').forEach(link => {
    link.addEventListener('click', () => {
        if (navMenu) {
            navMenu.classList.remove('active');
        }
    });
});

// Smooth Scrolling
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const targetId = this.getAttribute('href');
        if (targetId === '#') return;
        
        const target = document.querySelector(targetId);
        if (target) {
            const offsetTop = target.offsetTop - 100;
            window.scrollTo({
                top: offsetTop,
                behavior: 'smooth'
            });
        }
    });
});

// Subscription Plans Data
const plans = {
    light: {
        name: 'ЛАЙТ',
        price: 39,
        currency: '$',
        description: 'Самостоятельный тариф для начинающих'
    },
    start: {
        name: 'СТАРТ',
        price: 69,
        currency: '$',
        description: 'Для начинающих с поддержкой тренера'
    },
    optimal: {
        name: 'ОПТИМА',
        price: 119,
        currency: '$',
        description: 'Рекомендуемый тариф с регулярной поддержкой'
    },
    vip: {
        name: 'ПРЕМИУМ VIP',
        price: 299,
        currency: '$',
        description: 'Максимальное внимание и поддержка 24/7'
    }
};

// Modal Elements
const modal = document.getElementById('subscriptionModal');
const modalPlanName = document.getElementById('modalPlanName');
const modalPrice = document.getElementById('modalPrice');
const subscriptionForm = document.getElementById('subscriptionForm');
const modalClose = document.querySelector('.modal-close');

// Open Modal on Service Button Click
document.querySelectorAll('.btn-service').forEach(button => {
    button.addEventListener('click', () => {
        const planId = button.getAttribute('data-plan');
        const plan = plans[planId];
        
        if (plan && modal && modalPlanName && modalPrice) {
            modalPlanName.textContent = plan.name;
            modalPrice.textContent = `${plan.price} ${plan.currency || '$'}`;
            if (subscriptionForm) {
                subscriptionForm.setAttribute('data-plan', planId);
            }
            modal.style.display = 'block';
            document.body.style.overflow = 'hidden';
        }
    });
});

// Close Modal
if (modalClose) {
    modalClose.addEventListener('click', () => {
        if (modal) {
            modal.style.display = 'none';
            document.body.style.overflow = 'auto';
        }
    });
}

// Close Modal when clicking outside
if (modal) {
    window.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.style.display = 'none';
            document.body.style.overflow = 'auto';
        }
    });
}

// Handle Subscription Form Submission
if (subscriptionForm) {
    subscriptionForm.addEventListener('submit', (e) => {
        e.preventDefault();
        
        const formData = new FormData(subscriptionForm);
        const planId = subscriptionForm.getAttribute('data-plan');
        const plan = plans[planId];
        
        if (plan) {
            const data = {
                plan: plan.name,
                price: plan.price,
                name: formData.get('name'),
                email: formData.get('email'),
                phone: formData.get('phone')
            };
            
            // Here you would typically send this data to your backend
            console.log('Subscription Data:', data);
            
            // Show success message
            alert(`Спасибо, ${data.name}! Ваша заявка на подписку "${plan.name}" принята. Мы свяжемся с вами в ближайшее время.`);
            
            // Reset form and close modal
            subscriptionForm.reset();
            if (modal) {
                modal.style.display = 'none';
            }
            document.body.style.overflow = 'auto';
        }
    });
}

// Handle Goal Selection Form
const goalForm = document.querySelector('.goal-form');
if (goalForm) {
    goalForm.addEventListener('submit', (e) => {
        e.preventDefault();
        
        const selectedGoal = goalForm.querySelector('input[name="goal"]:checked');
        if (selectedGoal) {
            const goalText = selectedGoal.closest('.radio-label').querySelector('.radio-text').textContent;
            
            // Scroll to subscriptions section
            const subscriptionsSection = document.getElementById('subscriptions');
            if (subscriptionsSection) {
                const offsetTop = subscriptionsSection.offsetTop - 100;
                window.scrollTo({
                    top: offsetTop,
                    behavior: 'smooth'
                });
            }
            
            // You can store the selected goal for later use
            console.log('Selected goal:', goalText);
        } else {
            alert('Пожалуйста, выберите цель');
        }
    });
}

// Navbar Background on Scroll
window.addEventListener('scroll', () => {
    const navbar = document.querySelector('.navbar');
    if (navbar) {
        if (window.scrollY > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    }
});

// Intersection Observer for Fade-in Animations
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
        }
    });
}, observerOptions);

// Observe elements for animation
document.addEventListener('DOMContentLoaded', () => {
    const animatedElements = document.querySelectorAll('.service-card, .process-step, .goal-selection, .hero-content, .hero-image-container');
    
    animatedElements.forEach((el, index) => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(40px)';
        el.style.transition = `opacity 0.8s cubic-bezier(0.4, 0, 0.2, 1) ${index * 0.1}s, transform 0.8s cubic-bezier(0.4, 0, 0.2, 1) ${index * 0.1}s`;
        observer.observe(el);
    });
    
    // FAQ Accordion
    const faqItems = document.querySelectorAll('.faq-item');
    if (faqItems.length) {
        faqItems.forEach(item => {
            const questionButton = item.querySelector('.faq-question');
            const answer = item.querySelector('.faq-answer');

            if (questionButton && answer) {
                questionButton.addEventListener('click', () => {
                    const isExpanded = questionButton.getAttribute('aria-expanded') === 'true';

                    faqItems.forEach(otherItem => {
                        if (otherItem === item) {
                            return;
                        }
                        const otherButton = otherItem.querySelector('.faq-question');
                        const otherAnswer = otherItem.querySelector('.faq-answer');
                        if (otherButton && otherAnswer) {
                            otherItem.classList.remove('active');
                            otherButton.setAttribute('aria-expanded', 'false');
                        }
                    });

                    if (!isExpanded) {
                        item.classList.add('active');
                        questionButton.setAttribute('aria-expanded', 'true');
                    } else {
                        item.classList.remove('active');
                        questionButton.setAttribute('aria-expanded', 'false');
                    }
                });
            }
        });
    }
    
    // Parallax effect for hero image
    const heroImage = document.querySelector('.hero-image-container');
    if (heroImage) {
        let ticking = false;
        window.addEventListener('scroll', () => {
            if (!ticking) {
                window.requestAnimationFrame(() => {
                    const scrolled = window.pageYOffset;
                    const heroSection = document.querySelector('.hero');
                    if (heroSection) {
                        const heroHeight = heroSection.offsetHeight;
                        if (scrolled < heroHeight) {
                            const rate = scrolled * 0.2;
                            heroImage.style.transform = `translateY(${rate}px)`;
                        }
                    }
                    ticking = false;
                });
                ticking = true;
            }
        });
    }
});

// Service Card Hover Effects
document.querySelectorAll('.service-card').forEach(card => {
    card.addEventListener('mouseenter', () => {
        const priceElement = card.querySelector('.service-price');
        if (priceElement) {
            priceElement.style.transform = 'scale(1.05)';
            priceElement.style.transition = 'transform 0.3s ease';
        }
    });
    
    card.addEventListener('mouseleave', () => {
        const priceElement = card.querySelector('.service-price');
        if (priceElement) {
            priceElement.style.transform = 'scale(1)';
        }
    });
});

// Radio Button Custom Styling
document.querySelectorAll('.radio-input').forEach(radio => {
    radio.addEventListener('change', function() {
        // Remove checked state from all radios in the same group
        document.querySelectorAll(`input[name="${this.name}"]`).forEach(r => {
            r.closest('.radio-label').classList.remove('selected');
        });
        
        // Add selected class to current radio
        this.closest('.radio-label').classList.add('selected');
    });
});

// Interactive Before/After Slider - Optimized
document.addEventListener('DOMContentLoaded', () => {
    const resultSliders = document.querySelectorAll('.result-slider');
    
    resultSliders.forEach(slider => {
        const card = slider.closest('.result-card');
        const imageContainer = card.querySelector('.result-image-container');
        const beforeImage = card.querySelector('.result-image.result-before');
        const afterImage = card.querySelector('.result-image.result-after');
        const handle = card.querySelector('.result-slider-handle');
        const dividerLine = card.querySelector('.result-divider-line');
        
        if (!imageContainer || !beforeImage || !afterImage || !handle) return;
        
        let isDragging = false;
        let currentValue = 50;
        let rafId = null;
        let containerRect = null;
        
        // Use CSS custom properties for better performance
        imageContainer.style.setProperty('--slider-position', '50%');
        
        // Optimized update function using requestAnimationFrame
        const updateSlider = (value, immediate = false) => {
            currentValue = Math.max(0, Math.min(100, value));
            
            if (immediate) {
                // Cancel any pending animation frame
                if (rafId) {
                    cancelAnimationFrame(rafId);
                    rafId = null;
                }
                applyUpdate();
            } else {
                // Use requestAnimationFrame for smooth updates
                if (rafId === null) {
                    rafId = requestAnimationFrame(() => {
                        applyUpdate();
                        rafId = null;
                    });
                }
            }
        };
        
        const applyUpdate = () => {
            // Update slider value
            slider.value = currentValue;
            
            // Use CSS custom property for better performance
            const percentage = currentValue;
            imageContainer.style.setProperty('--slider-position', `${percentage}%`);
            
            // Update clip paths - inverted logic: right = AFTER, left = BEFORE
            // When percentage = 0 (left): show 100% BEFORE, hide AFTER
            // When percentage = 100 (right): hide BEFORE, show 100% AFTER
            beforeImage.style.clipPath = `inset(0 ${percentage}% 0 0)`;
            afterImage.style.clipPath = `inset(0 0 0 ${100 - percentage}%)`;
            
            // Update handle position using left (simpler and performant)
            handle.style.left = `${percentage}%`;
            
            // Update divider line position to move with handle
            if (dividerLine) {
                dividerLine.style.left = `${percentage}%`;
            }
        };
        
        // Calculate position from event
        const getPositionFromEvent = (clientX) => {
            if (!containerRect) {
                containerRect = imageContainer.getBoundingClientRect();
            }
            const x = clientX - containerRect.left;
            const percentage = (x / containerRect.width) * 100;
            return percentage;
        };
        
        // Reset container rect on resize
        const resetRect = () => {
            containerRect = null;
        };
        
        window.addEventListener('resize', resetRect);
        
        // Mouse events
        const handleMouseDown = (e) => {
            isDragging = true;
            containerRect = imageContainer.getBoundingClientRect();
            imageContainer.style.cursor = 'grabbing';
            imageContainer.style.userSelect = 'none';
            const percentage = getPositionFromEvent(e.clientX);
            updateSlider(percentage, true);
            e.preventDefault();
        };
        
        const handleMouseMove = (e) => {
            if (!isDragging) return;
            const percentage = getPositionFromEvent(e.clientX);
            updateSlider(percentage);
        };
        
        const handleMouseUp = () => {
            if (isDragging) {
                isDragging = false;
                imageContainer.style.cursor = 'grab';
                imageContainer.style.userSelect = '';
            }
        };
        
        // Touch events
        const handleTouchStart = (e) => {
            isDragging = true;
            containerRect = imageContainer.getBoundingClientRect();
            const percentage = getPositionFromEvent(e.touches[0].clientX);
            updateSlider(percentage, true);
            e.preventDefault();
        };
        
        const handleTouchMove = (e) => {
            if (!isDragging) return;
            const percentage = getPositionFromEvent(e.touches[0].clientX);
            updateSlider(percentage);
            e.preventDefault();
        };
        
        const handleTouchEnd = () => {
            isDragging = false;
        };
        
        // Slider input event (for accessibility)
        slider.addEventListener('input', (e) => {
            updateSlider(parseFloat(e.target.value), true);
        });
        
        // Image container drag
        imageContainer.addEventListener('mousedown', handleMouseDown);
        document.addEventListener('mousemove', handleMouseMove, { passive: true });
        document.addEventListener('mouseup', handleMouseUp);
        document.addEventListener('mouseleave', handleMouseUp);
        
        imageContainer.addEventListener('touchstart', handleTouchStart, { passive: false });
        imageContainer.addEventListener('touchmove', handleTouchMove, { passive: false });
        imageContainer.addEventListener('touchend', handleTouchEnd, { passive: true });
        imageContainer.addEventListener('touchcancel', handleTouchEnd, { passive: true });
        
        // Handle drag
        handle.addEventListener('mousedown', (e) => {
            isDragging = true;
            containerRect = imageContainer.getBoundingClientRect();
            e.preventDefault();
            e.stopPropagation();
        });
        
        // Reset on double click
        imageContainer.addEventListener('dblclick', () => {
            updateSlider(50, true);
        });
        
        // Initialize
        updateSlider(50, true);
    });
});
