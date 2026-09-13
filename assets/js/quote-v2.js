
(function() {
  const MAX_ATTACHMENT_BYTES = 10 * 1024 * 1024;

  function initInquiryForm(formId, config) {
    const form = document.getElementById(formId);
    if (!form) return;

    const dropZone = document.getElementById(config.dropZoneId);
    const fileInput = form.querySelector('.file-input-multi');
    const fileList = document.getElementById(config.fileListId);
    let attachments = [];
    let attachmentError = '';

    const attachmentStatus = document.createElement('p');
    attachmentStatus.className = 'attachment-status';
    attachmentStatus.setAttribute('role', 'status');
    attachmentStatus.setAttribute('aria-live', 'polite');
    attachmentStatus.style.cssText = 'margin:10px 0 0; font-size:13px; color:var(--muted);';
    if (fileList) fileList.insertAdjacentElement('afterend', attachmentStatus);

    function formatBytes(bytes) {
      return `${(bytes / (1024 * 1024)).toFixed(2)}MB`;
    }

    function totalAttachmentBytes(files) {
      return files.reduce((total, file) => total + file.size, 0);
    }

    function updateAttachmentStatus(errorMessage) {
      if (!attachmentStatus) return;
      if (errorMessage) {
        attachmentError = errorMessage;
        attachmentStatus.textContent = errorMessage;
        attachmentStatus.style.color = '#b42318';
        return;
      }
      attachmentError = '';
      const total = totalAttachmentBytes(attachments);
      attachmentStatus.textContent = attachments.length
        ? `${attachments.length} file${attachments.length === 1 ? '' : 's'} selected · ${formatBytes(total)} of 10MB`
        : 'Multiple files allowed · 10MB total maximum';
      attachmentStatus.style.color = 'var(--muted)';
    }

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
      if (!fileList) return;
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
          updateAttachmentStatus();
        };
        
        item.appendChild(removeBtn);
        fileList.appendChild(item);
      });
    }

    function handleFiles(files) {
      const nextAttachments = attachments.slice();
      Array.from(files).forEach(file => {
        if (!nextAttachments.some(a => a.name === file.name && a.size === file.size)) {
          nextAttachments.push(file);
        }
      });

      const total = totalAttachmentBytes(nextAttachments);
      if (total > MAX_ATTACHMENT_BYTES) {
        updateAttachmentStatus(`Files were not added: ${formatBytes(total)} exceeds the 10MB total limit.`);
        if (fileInput) fileInput.value = '';
        return;
      }

      attachments = nextAttachments;
      updateFileList();
      updateAttachmentStatus();
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

    function prepareNativeAttachments() {
      form.querySelectorAll('[data-native-attachment]').forEach(input => input.remove());

      attachments.forEach((file, index) => {
        const transfer = new DataTransfer();
        transfer.items.add(file);

        const input = document.createElement('input');
        input.type = 'file';
        input.name = index === 0 ? 'attachment' : `attachment${index + 1}`;
        input.hidden = true;
        input.dataset.nativeAttachment = 'true';
        input.files = transfer.files;
        form.appendChild(input);
      });
    }

    // FormSubmit's AJAX endpoint accepts the text fields but drops attachments.
    // Submit through the verified multipart endpoint so every selected file is emailed.
    form.onsubmit = (e) => {
      e.preventDefault();
      const btn = form.querySelector('button[type="submit"]');
      const originalText = btn.innerHTML;

      if (attachmentError || totalAttachmentBytes(attachments) > MAX_ATTACHMENT_BYTES) {
        updateAttachmentStatus(attachmentError || 'Please keep all attachments within the 10MB total limit.');
        return;
      }

      try {
        prepareNativeAttachments();
      } catch (error) {
        updateAttachmentStatus('This browser could not prepare the attachments. Please select the files again or email sales@qulacrafts.com.');
        btn.disabled = false;
        btn.innerHTML = originalText;
        return;
      }

      btn.disabled = true;
      btn.innerHTML = 'Sending...';
      HTMLFormElement.prototype.submit.call(form);
    };

    updateAttachmentStatus();
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
