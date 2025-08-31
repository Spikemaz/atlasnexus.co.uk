// Smooth Keyboard Scrolling Module for AtlasNexus
(function() {
    'use strict';
    
    // Configuration - Smoother and slower settings
    const config = {
        scrollSpeed: 20, // Reduced from 40 - Pixels per key press
        smoothDuration: 400, // Increased from 200 - Animation duration in ms for smoother transitions
        continuousScrollSpeed: 3, // Reduced from 8 - Much slower speed for held keys
        scrollAcceleration: 1.02, // Reduced from 1.05 - Slower acceleration when holding
        maxScrollSpeed: 25, // Reduced from 50 - Lower maximum scroll speed
        debounceDelay: 15 // Increased from 10 - More debounce for smoother scrolling
    };
    
    // State management
    let isScrolling = false;
    let scrollVelocity = 0;
    let scrollDirection = 0;
    let animationFrame = null;
    let keyHoldTimer = null;
    let currentScrollSpeed = config.continuousScrollSpeed;
    let lastScrollTime = 0;
    
    // Key states
    const keyStates = {
        ArrowUp: false,
        ArrowDown: false,
        PageUp: false,
        PageDown: false
    };
    
    // Smooth scroll animation
    function smoothScrollTo(targetY, duration = config.smoothDuration) {
        const startY = window.pageYOffset;
        const distance = targetY - startY;
        const startTime = performance.now();
        
        function animate(currentTime) {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            // Easing function (ease-in-out-sine for smoother transitions)
            const easeProgress = -(Math.cos(Math.PI * progress) - 1) / 2;
            
            window.scrollTo(0, startY + distance * easeProgress);
            
            if (progress < 1) {
                requestAnimationFrame(animate);
            }
        }
        
        requestAnimationFrame(animate);
    }
    
    // Continuous scroll for held keys
    function continuousScroll() {
        if (!isScrolling) return;
        
        const now = performance.now();
        const deltaTime = Math.min(now - lastScrollTime, 100) / 16.67; // Normalize to 60fps
        lastScrollTime = now;
        
        // Apply acceleration when holding
        if (keyStates.ArrowUp || keyStates.ArrowDown) {
            currentScrollSpeed = Math.min(
                currentScrollSpeed * config.scrollAcceleration,
                config.maxScrollSpeed
            );
        }
        
        // Calculate scroll amount
        const scrollAmount = currentScrollSpeed * scrollDirection * deltaTime;
        
        // Apply smooth scrolling
        const currentY = window.pageYOffset;
        const targetY = currentY + scrollAmount;
        
        // Clamp to document bounds
        const maxScroll = document.documentElement.scrollHeight - window.innerHeight;
        const clampedY = Math.max(0, Math.min(targetY, maxScroll));
        
        window.scrollTo({
            top: clampedY,
            behavior: 'instant' // Use instant for continuous scrolling
        });
        
        // Continue animation
        animationFrame = requestAnimationFrame(continuousScroll);
    }
    
    // Handle keydown events
    function handleKeyDown(e) {
        // Check if we're in an input field or contenteditable
        const activeElement = document.activeElement;
        if (activeElement && (
            activeElement.tagName === 'INPUT' ||
            activeElement.tagName === 'TEXTAREA' ||
            activeElement.tagName === 'SELECT' ||
            activeElement.contentEditable === 'true'
        )) {
            return;
        }
        
        // Handle navigation keys
        switch(e.key) {
            case 'ArrowUp':
            case 'ArrowDown':
                if (!keyStates[e.key]) {
                    e.preventDefault();
                    keyStates[e.key] = true;
                    
                    // Set scroll direction
                    scrollDirection = e.key === 'ArrowUp' ? -1 : 1;
                    
                    // Start continuous scrolling
                    if (!isScrolling) {
                        isScrolling = true;
                        currentScrollSpeed = config.continuousScrollSpeed;
                        lastScrollTime = performance.now();
                        continuousScroll();
                    }
                }
                break;
                
            case 'PageUp':
            case 'PageDown':
                e.preventDefault();
                keyStates[e.key] = true;
                
                // Calculate scroll distance (one viewport height)
                const viewportHeight = window.innerHeight;
                const scrollDistance = viewportHeight * 0.75; // Reduced from 90% to 75% for more control
                const direction = e.key === 'PageUp' ? -1 : 1;
                
                // Smooth scroll to target with longer duration
                const currentY = window.pageYOffset;
                const targetY = currentY + (scrollDistance * direction);
                smoothScrollTo(targetY, 600); // Increased from 300 for smoother page scrolling
                break;
                
            case 'Home':
                e.preventDefault();
                smoothScrollTo(0, 500);
                break;
                
            case 'End':
                e.preventDefault();
                const maxScroll = document.documentElement.scrollHeight - window.innerHeight;
                smoothScrollTo(maxScroll, 500);
                break;
        }
    }
    
    // Handle keyup events
    function handleKeyUp(e) {
        if (keyStates.hasOwnProperty(e.key)) {
            keyStates[e.key] = false;
            
            // Stop continuous scrolling if no arrow keys are pressed
            if (e.key === 'ArrowUp' || e.key === 'ArrowDown') {
                if (!keyStates.ArrowUp && !keyStates.ArrowDown) {
                    isScrolling = false;
                    scrollDirection = 0;
                    
                    // Cancel animation frame
                    if (animationFrame) {
                        cancelAnimationFrame(animationFrame);
                        animationFrame = null;
                    }
                    
                    // Apply smooth deceleration with reduced momentum
                    const currentY = window.pageYOffset;
                    const momentum = currentScrollSpeed * scrollDirection * 2; // Reduced from 5 for smoother stop
                    smoothScrollTo(currentY + momentum, 300); // Increased duration for smoother deceleration
                }
            }
        }
    }
    
    // Handle visibility change (pause when tab is not visible)
    function handleVisibilityChange() {
        if (document.hidden) {
            // Reset all key states when tab becomes hidden
            Object.keys(keyStates).forEach(key => {
                keyStates[key] = false;
            });
            isScrolling = false;
            scrollDirection = 0;
            
            if (animationFrame) {
                cancelAnimationFrame(animationFrame);
                animationFrame = null;
            }
        }
    }
    
    // Handle window blur (reset states when window loses focus)
    function handleWindowBlur() {
        Object.keys(keyStates).forEach(key => {
            keyStates[key] = false;
        });
        isScrolling = false;
        scrollDirection = 0;
        
        if (animationFrame) {
            cancelAnimationFrame(animationFrame);
            animationFrame = null;
        }
    }
    
    // Initialize smooth scrolling
    function init() {
        // Add event listeners
        document.addEventListener('keydown', handleKeyDown);
        document.addEventListener('keyup', handleKeyUp);
        document.addEventListener('visibilitychange', handleVisibilityChange);
        window.addEventListener('blur', handleWindowBlur);
        
        // Add smooth scroll behavior to all internal links
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function(e) {
                const targetId = this.getAttribute('href');
                if (targetId && targetId !== '#') {
                    const targetElement = document.querySelector(targetId);
                    if (targetElement) {
                        e.preventDefault();
                        const targetY = targetElement.offsetTop;
                        smoothScrollTo(targetY, 500);
                    }
                }
            });
        });
        
        // Add CSS for smooth scrolling
        if (!document.getElementById('smooth-scroll-styles')) {
            const style = document.createElement('style');
            style.id = 'smooth-scroll-styles';
            style.textContent = `
                /* Smooth scroll enhancement styles */
                html {
                    scroll-behavior: smooth;
                }
                
                /* Hide scrollbar during smooth scroll for cleaner appearance */
                .smooth-scrolling::-webkit-scrollbar {
                    width: 12px;
                }
                
                .smooth-scrolling::-webkit-scrollbar-track {
                    background: rgba(0, 0, 0, 0.1);
                }
                
                .smooth-scrolling::-webkit-scrollbar-thumb {
                    background: rgba(96, 165, 250, 0.5);
                    border-radius: 6px;
                    transition: background 0.3s ease;
                }
                
                .smooth-scrolling::-webkit-scrollbar-thumb:hover {
                    background: rgba(96, 165, 250, 0.8);
                }
                
                /* Focus styles for keyboard navigation */
                *:focus-visible {
                    outline: 2px solid rgba(96, 165, 250, 0.5);
                    outline-offset: 2px;
                    border-radius: 4px;
                }
            `;
            document.head.appendChild(style);
        }
        
        // Add smooth-scrolling class to body
        document.body.classList.add('smooth-scrolling');
    }
    
    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
    
    // Export for use in other modules if needed
    window.SmoothScroll = {
        config: config,
        smoothScrollTo: smoothScrollTo,
        init: init
    };
})();