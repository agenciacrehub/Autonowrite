// Initialize form validation
function initFormValidation() {
    const forms = document.querySelectorAll('.needs-validation');
    
    // Add validation to all forms
    Array.from(forms).forEach(form => {
        // Handle form submission
        form.addEventListener('submit', function(event) {
            const clickedButton = document.activeElement;
            
            // If back button is clicked, allow form submission without validation
            if (clickedButton && clickedButton.name === 'back') {
                form.noValidate = true; // Disable HTML5 validation for back button
                return true;
            }
            
            // For next/submit buttons, validate the form
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
                
                // Show validation messages for all invalid fields
                const invalidFields = form.querySelectorAll(':invalid');
                invalidFields.forEach(field => {
                    field.classList.add('is-invalid');
                    const feedback = field.nextElementSibling;
                    if (feedback && feedback.classList.contains('invalid-feedback')) {
                        feedback.style.display = 'block';
                    }
                });
                
                // Scroll to first invalid field
                if (invalidFields.length > 0) {
                    invalidFields[0].scrollIntoView({ behavior: 'smooth', block: 'center' });
                }
                
                form.classList.add('was-validated');
                return false;
            }
            
            // If form is valid, show loading state and allow submission
            const submitButton = form.querySelector('button[type="submit"]:not([name="back"])');
            if (submitButton) {
                submitButton.disabled = true;
                const originalText = submitButton.innerHTML;
                submitButton.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>Processando...';
                
                // Revert button state if form submission fails
                setTimeout(() => {
                    submitButton.disabled = false;
                    submitButton.innerHTML = originalText;
                }, 10000); // 10 second timeout
            }
            
            form.classList.add('was-validated');
        }, false);
        
        // Add real-time validation on input
        form.querySelectorAll('input, select, textarea').forEach(input => {
            input.addEventListener('input', function() {
                if (this.checkValidity()) {
                    this.classList.remove('is-invalid');
                    this.classList.add('is-valid');
                    
                    const feedback = this.nextElementSibling;
                    if (feedback && feedback.classList.contains('invalid-feedback')) {
                        feedback.style.display = 'none';
                    }
                } else {
                    this.classList.remove('is-valid');
                    this.classList.add('is-invalid');
                }
            });
            
            // Handle blur for required fields
            if (input.required) {
                input.addEventListener('blur', function() {
                    if (!this.value.trim()) {
                        this.classList.add('is-invalid');
                    }
                });
            }
        });
    });
    
    // Initialize tooltips if Bootstrap is available
    if (typeof bootstrap !== 'undefined') {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.forEach(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
}

// Initialize rich text editors
function initRichTextEditors() {
    const richTextEditors = document.querySelectorAll('.rich-text-editor');
    
    if (typeof Quill !== 'undefined' && richTextEditors.length > 0) {
        richTextEditors.forEach(editor => {
            const quill = new Quill(editor, {
                theme: 'snow',
                modules: {
                    toolbar: [
                        ['bold', 'italic', 'underline', 'strike'],
                        ['blockquote', 'code-block'],
                        [{ 'header': 1 }, { 'header': 2 }],
                        [{ 'list': 'ordered'}, { 'list': 'bullet' }],
                        [{ 'script': 'sub'}, { 'script': 'super' }],
                        [{ 'indent': '-1'}, { 'indent': '+1' }],
                        [{ 'direction': 'rtl' }],
                        [{ 'size': ['small', false, 'large', 'huge'] }],
                        [{ 'header': [1, 2, 3, 4, 5, 6, false] }],
                        [{ 'color': [] }, { 'background': [] }],
                        [{ 'font': [] }],
                        [{ 'align': [] }],
                        ['clean'],
                        ['link', 'image', 'video']
                    ]
                },
                placeholder: 'Digite seu conteúdo aqui...',
                bounds: editor.parentElement
            });
            
            // Update hidden input when editor content changes
            quill.on('text-change', function() {
                const hiddenInput = document.getElementById(editor.dataset.target);
                if (hiddenInput) {
                    hiddenInput.value = quill.root.innerHTML;
                    hiddenInput.dispatchEvent(new Event('input'));
                }
            });
        });
    }
}

// Initialize everything when the DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initFormValidation();
    initRichTextEditors();
});
