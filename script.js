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
    workouts: {
        name: 'ОНЛАЙН+ ТРЕНИРОВКИ',
        price: 3890,
        description: 'Персональная программа тренировок'
    },
    nutrition: {
        name: 'ПИТАНИЕ',
        price: 2890,
        description: 'Персональный план питания'
    },
    premium: {
        name: 'ПРЕМИУМ ПАКЕТ ТРЕНИРОВКИ + ПИТАНИЕ',
        price: 5890,
        description: 'Комплексный подход с поддержкой тренера'
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
            modalPrice.textContent = `${plan.price} ₽`;
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
