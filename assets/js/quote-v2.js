
(function() {
  function initInquiryForm(formId, config) {
    const form = document.getElementById(formId);
    if (!form) return;

    const dropZone = document.getElementById(config.dropZoneId);
    const fileInput = form.querySelector('.file-input-multi');
    const fileList = document.getElementById(config.fileListId);
    let attachments = [];

    // --- URL Parameters Auto-fill (Only for specific forms if needed) ---
    if (config.isDedicatedPage) {
      const params = new URLSearchParams(window.location.search);
      const pName = params.get('product');
      const pSku = params.get('sku');
      const pImg = params.get('image');
      
      const previewEl = document.getElementById('selectedProduct');
      if (previewEl && (pName || pSku)) {
        previewEl.style.display = 'block';
        document.getElementById('pPreviewTitle').textContent = pName || 'Product Inquiry';
        document.getElementById('pPreviewSku').textContent = pSku ? `SKU: ${pSku}` : '';
        if (pImg) document.getElementById('pPreviewImg').src = pImg;
        
        document.getElementById('hiddenSku').value = pSku || '';
        document.getElementById('hiddenUrl').value = window.location.href;
        
        const productSelect = form.querySelector('select[name="product"]');
        if (pSku && productSelect) {
          if (pSku.startsWith('RW')) productSelect.value = 'Resin Charms';
          else if (pSku.startsWith('YX') || pSku.startsWith('YM')) productSelect.value = 'Polymer Clay Sprinkles';
          else if (pSku.startsWith('CZB')) productSelect.value = 'Acrylic Beads';
          else if (pSku.startsWith('CDK')) productSelect.value = 'Keychains';
        }
        const messageEl = form.querySelector('textarea[name="message"]');
        if (messageEl) {
          const productNote = `I am interested in ${pName || pSku}. Please provide a quote based on the following requirements:\n\n`;
          messageEl.value = messageEl.value ? (messageEl.value + '\n' + productNote) : productNote;
        }
      }
    }

    // --- Attachment Handling ---
    function updateFileList() {
      fileList.innerHTML = '';
      attachments.forEach((file, index) => {
        const item = document.createElement('div');
        item.className = 'file-item';
        
        if (file.type.startsWith('image/')) {
          const img = document.createElement('img');
          img.src = URL.createObjectURL(file);
          item.appendChild(img);
        } else {
          const info = document.createElement('div');
          info.className = 'file-info';
          info.innerHTML = `<b>${file.name.split('.').pop().toUpperCase()}</b><br>${(file.size/1024).toFixed(1)}KB`;
          item.appendChild(info);
        }
        
        const removeBtn = document.createElement('button');
        removeBtn.innerHTML = '&times;';
        removeBtn.className = 'file-remove';
        removeBtn.onclick = (e) => {
          e.preventDefault();
          attachments.splice(index, 1);
          updateFileList();
        };
        
        item.appendChild(removeBtn);
        fileList.appendChild(item);
      });
    }

    function handleFiles(files) {
      Array.from(files).forEach(file => {
        if (!attachments.some(a => a.name === file.name && a.size === file.size)) {
          attachments.push(file);
        }
      });
      updateFileList();
    }

    if (fileInput) fileInput.onchange = (e) => handleFiles(e.target.files);

    if (dropZone) {
      dropZone.ondragover = (e) => { e.preventDefault(); dropZone.classList.add('dragover'); };
      dropZone.ondragleave = () => dropZone.classList.remove('dragover');
      dropZone.ondrop = (e) => {
        e.preventDefault();
        dropZone.classList.remove('dragover');
        handleFiles(e.dataTransfer.files);
      };
    }

    // Global paste but only process if this form was recently interacted with or is visible
    window.addEventListener('paste', (e) => {
      // Check if this form is visible or focused
      const rect = form.getBoundingClientRect();
      const isVisible = (rect.top >= 0 && rect.bottom <= window.innerHeight);
      if (!isVisible && document.activeElement.closest('form') !== form) return;
      
      if (document.activeElement.tagName === 'TEXTAREA' || document.activeElement.tagName === 'INPUT') {
          // If it's the message area, we still want to allow pasting images into attachments
          if (document.activeElement.name !== 'message') return;
      }

      const items = e.clipboardData.items;
      for (let i = 0; i < items.length; i++) {
        if (items[i].type.indexOf('image') !== -1) {
          const file = items[i].getAsFile();
          const renamedFile = new File([file], `pasted-image-${Date.now()}.png`, { type: 'image/png' });
          handleFiles([renamedFile]);
        }
      }
    });

    // --- Form Submission ---
    form.onsubmit = async (e) => {
      e.preventDefault();
      const btn = form.querySelector('button[type="submit"]');
      const originalText = btn.innerHTML;
      
      btn.disabled = true;
      btn.innerHTML = 'Sending...';

      const formData = new FormData(form);
      attachments.forEach(file => {
        formData.append('attachments[]', file);
      });

      try {
        const ajaxEndpoint = form.action.includes('/ajax/')
          ? form.action
          : form.action.replace('https://formsubmit.co/', 'https://formsubmit.co/ajax/');

        const response = await fetch(ajaxEndpoint, {
          method: 'POST',
          body: formData,
          headers: { 'Accept': 'application/json' }
        });

        if (response.ok) {
          form.innerHTML = `
            <div style="text-align:center; padding:60px 20px;">
              <div style="font-size:64px; margin-bottom:20px;">✓</div>
              <h2 style="font-family:var(--serif); font-size:32px;">Inquiry Received</h2>
              <p style="color:var(--muted); font-size:18px; margin:15px 0 30px;">
                Thank you for choosing Qula Craft. Our sales team will get back to you within 3-12 hours with a detailed quote.
              </p>
              <a href="index.html" class="btn btn-primary">Refresh Form</a>
            </div>
          `;
          window.scrollTo({ top: form.offsetTop - 150, behavior: 'smooth' });
        } else {
          throw new Error('Submission failed');
        }
      } catch (err) {
        alert('Sorry, there was an error sending your inquiry. Please try again or email us directly at sales@qulacrafts.com');
        btn.disabled = false;
        btn.innerHTML = originalText;
      }
    };
  }

  // Initialize both forms
  initInquiryForm('inquiryForm', {
    dropZoneId: 'dropZone',
    fileListId: 'fileList',
    isDedicatedPage: true
  });

  initInquiryForm('inquiryFormHome', {
    dropZoneId: 'dropZoneHome',
    fileListId: 'fileListHome',
    isDedicatedPage: false
  });

})();
