$(function() {
    
    pdfjsLib.GlobalWorkerOptions.workerSrc = "/static/js/pdf.worker.min.js";
    var PIXEL_RATIO = (function () {
        var dpr = window.devicePixelRatio || 1;
        var contex = document.createElement('canvas').getContext('2d');
        var bspr = contex.backingStorePixelRatio || 
                  contex.oBackingStorePixelRatio ||
                  contex.webkitBackingStorePixelRatio ||
                  contex.mozBackingStorePixelRatio ||
                  contex.msBackingStorePixelRatio || 1;
        return dpr / bspr;})();
    var refresh_count = 0;
    var IN_LANG = $('#in-lang').val();
    var LS_KEY_IN = 'in.juben.editor.txt'; 
    var in_text = $('#in-juben-text')[0];
    var in_placeholder = $('#in-juben-text').attr('placeholder');
    var pdf_container = $('#pdf-container');
    var injuben_result;
    var default_layout = get_cookie('in.layout.option');
    if( default_layout === undefined) default_layout = 1;
    $('#in-juben-text').val(get_local_storage(LS_KEY_IN));
	var in_editor = CodeMirror.fromTextArea(in_text, {
      mode: 'markdown',
      lineNumbers: true,
      lineWrapping: true,
      foldGutter: true,
      gutters: ['CodeMirror-linenumbers', 'CodeMirror-foldgutter'],
      scrollbarStyle: 'simple',
      theme: 'idea'
    });
    
    in_editor.on('change', function(cm) {
        if(!$('#in-refresh-preview').hasClass('is-loading')) $('#in-refresh-preview').attr('disabled', false);
        word_count(cm);
    });

    $('#in-juben-text').bind('input propertychange', function() {
        in_editor.setValue($(this).val());
    });

    $(document).keydown(function(event) {
        if((event.ctrlKey || event.metaKey) && event.which == 83) {
            event.preventDefault();
            save_in_to_local_storage();
            if($('#in-refresh-preview').attr('disabled')) return false;
            submit_preview();
            return false;
        }else if(event.key === "Escape") {
            exit_modal();
        }
    });
   
    $(window).bind('beforeunload', function(){
        save_state();
    });
    
    $(window).on('resize', function(){in_resize();});

    window.addEventListener("pagehide", function(evt){
        save_state();
    }, false);

    $('body').on('click', function() {
        if($('#in-preview-navbar').hasClass('is-active')) $('#in-preview-navbar').removeClass('is-active');
        if(!$('#in-preview-settings-menu').hasClass('in-preview-settings-menu')) $('#in-preview-settings-menu').addClass('in-preview-settings-menu');
    });

    $('#in-brand').on('click touchstart', function() {
        $('#in-navbar-dropdown-menu').toggleClass("is-hidden-touch");
        return false;
    });

    $('#in-dark-mode').on('click', function(){
        set_editor_night_mode($(this));
    });

    $('#in-active-line').on('click', function(){
        set_editor_active_line($(this));
    });

    $('input:radio[name="in-font-size"]').change(function(){
        set_editor_font_size($(this));
    });

    $('#in-has-scene-num').on('click', function(){
        set_preview_has_scene_num($(this));
    });

    $('#in-strong-scene-heading').on('click', function(){
        set_preview_strong_scene_heading($(this));
    });

    $('#in-first-page-num').on('click', function(){
        set_preview_first_page_num($(this));
    });

    $('.menu-modal').on('click', function() {
        $('#'+$(this).attr('data-target')).addClass('is-active');
        event.stopImmediatePropagation();
    });

    $('.modal .delete').on('click', function(event) {
        event.preventDefault();
        exit_modal();
    });

    $('.modal-background').on('click', function(){
        exit_modal();
    });

    $('#in-save-txt').on('click', function() {
        var content = in_editor.getValue().trim(); 
        file_name = content.split("\n")[0].trim().replace('Title:','').trim();
        if(file_name === '') file_name = 'injuben';
        download(content, file_name + ".txt", "text/plain");
    });

    $('#in-collaps-bar').on('click', function(){
        $('#in-preview-panel').toggleClass('column').toggle();
        if($('#in-preview-panel').hasClass('column')) {
            $('#in-collaps-arrow').html('&#x25B6;');
            set_cookie('in.layout.option', 1);
        }
        else {
            $('#in-collaps-arrow').html('&#x25C0;');
            set_cookie('in.layout.option', 2);
        }
        if(default_layout === '2') {
          render_pdf(pdf_container, injuben_result.content);
          default_layout = 1;
        }
    });

    $('#in-ec-pdf').on('click', function(){
        $(this).addClass('is-disabled').toggleClass('fi-arrows-expand').toggleClass('fi-arrows-compress');
        $('#in-edit-panel').toggleClass('column').toggle();
        $('#in-collaps-bar').toggleClass('column').toggle();
        $('#in-preview-panel').toggleClass('is-12');
        if($('#in-preview-panel').hasClass('is-12')) {
            render_pdf(pdf_container, injuben_result.content, true, 0.8);
        }else {
            render_pdf(pdf_container, injuben_result.content);
        }
    });

    $('#in-preview-settings-menu').on('click', function(event){
        if($('#in-refresh-preview').attr('disabled')) return false; 
        $('#in-preview-navbar').toggleClass('is-active');
        event.stopImmediatePropagation();
    });

    $('#in-preview-settings-menu').mouseenter(function(event){
        event.stopImmediatePropagation();
    });

    $('#in-preview-settings').on('click', function(event){
        event.stopImmediatePropagation();
    });

    $('#in-form').submit(function(event) {
        submit_form(this, event);
    });

    $('#in-refresh-preview').on('click', function(){
        if($(this).attr('disabled')) return false; 
        submit_preview();
        event.stopImmediatePropagation();
    });

    $('#in-save-pdf').on('click', function(e) {
        if($(this).attr('disabled')) return false;
        download('data:application/pdf;base64,' + injuben_result.content, injuben_result.filename + '.' + injuben_result.suffix, 'application/pdf');
    });

    load_layout();
    in_resize();
    load_modal();
    word_count(in_editor);
    load_editor_option();
    load_preview_option();
    load_state();
    if(in_editor.getValue().trim() !== '')  submit_preview();
    
    function load_editor_option() {
        if(get_cookie('in.editor.option.theme') === 'dracula') {
            $('#in-dark-mode').prop('checked', true); 
        } else {
            $('#in-dark-mode').prop('checked', false); 
        }
        set_editor_night_mode($('#in-dark-mode'));

        if(get_cookie('in.editor.option.styleActiveLine') === 'true') {
            $('#in-active-line').prop('checked', true); 
        } else {
            $('#in-active-line').prop('checked', false); 
        }
        set_editor_active_line($('#in-active-line'));

        $('input:radio[name="in-font-size"]').each(function(){
            if(get_cookie('in.editor.option.fontSize') === undefined) {
                if($(this).is(':checked'))
                    set_editor_font_size($(this));
            }
            else if(get_cookie('in.editor.option.fontSize') === $(this).val()) {
                $(this).prop('checked', true);
                set_editor_font_size($(this));
            }
        });
    }

    function load_preview_option() {
        if(get_cookie('in.preview.option.hasSceneNum') === 'false') {
            $('#in-has-scene-num').prop('checked', false);
        } 
        else if(get_cookie('in.preview.option.hasSceneNum') === 'true') {
            $('#in-has-scene-num').prop('checked', true); 
        } 

        if(get_cookie('in.preview.option.strongSceneHeading') === 'false') {
            $('#in-strong-scene-heading').prop('checked', false);
        } 
        else if(get_cookie('in.preview.option.strongSceneHeading') === 'true') {
            $('#in-strong-scene-heading').prop('checked', true);
        }

        if(get_cookie('in.preview.option.firstPageNum') === 'false') {
            $('#in-first-page-num').prop('checked', false);
        } 
        else if(get_cookie('in.preview.option.firstPageNum') === 'true') {
            $('#in-first-page-num').prop('checked', true);
        }  

        if(injuben_result === undefined) {
             $('#in-save-pdf').attr('disabled', true);
        }

        if(injuben_result === undefined) {
             $('#in-ec-pdf').addClass('is-disabled');
        }

    }

    function load_state() {
        in_editor.focus();
        var in_coursor = JSON.parse(get_cookie('in.editor.state.coursor'));
        in_editor.setCursor(in_coursor);
        var in_scroll_info = JSON.parse(get_cookie('in.editor.state.scroll'));
        in_editor.scrollTo(0, in_scroll_info.top);
    }

    function load_layout() {
        if(get_cookie('in.layout.option') === '2') {
            $('#in-preview-panel').removeClass('column').hide(); 
            $('#in-edit-panel').removeClass('in-hidden');
            $('#in-collaps-arrow').html('&#x25C0;'); 
        }
    }

    function load_modal() {
        if(location.href.indexOf('#help') !== -1) {
            $('#in-help').addClass('is-active');
        }
    }

    function exit_modal() {
        $('.modal').each(function() {$(this).removeClass('is-active');});
        if(location.href.indexOf('#') !== -1) {
            location.href = '#';
        }
    }

    function save_state() {
        save_in_to_local_storage();
        set_cookie('in.editor.state.coursor', JSON.stringify(in_editor.getCursor()));
        set_cookie('in.editor.state.scroll', JSON.stringify(in_editor.getScrollInfo()));
        set_cookie('in.preview.state.scrollTop', $('#in-preview-container').scrollTop());
    }

    function set_editor_night_mode(el) {
        if(el.is(':checked')) {
            in_editor.setOption("theme", 'dracula');
            set_cookie('in.editor.option.theme','dracula');
        }
        else {
            in_editor.setOption("theme", 'idea');
            set_cookie('in.editor.option.theme','idea');
        }
    }

    function set_editor_active_line(el) {
        if(el.is(':checked')) {
            in_editor.setOption('styleActiveLine', true);
            set_cookie('in.editor.option.styleActiveLine','true');
        }
        else {
            in_editor.setOption('styleActiveLine', false);
            set_cookie('in.editor.option.styleActiveLine','false');
        }
    }

    function set_editor_font_size(el) {
        if (el.is(':checked')){
            switch(el.val()) {
                case 'small':
                    $('.CodeMirror').each(function(index, el) { $(el).addClass('in-small-font').removeClass('in-large-font'); });
                    set_cookie('in.editor.option.fontSize','small');
                    break;
                case 'large':
                    $('.CodeMirror').each(function(index, el) { $(el).addClass('in-large-font').removeClass('in-small-font'); });
                    set_cookie('in.editor.option.fontSize','large');
                    break;
                case 'medium':
                default:
                    $('.CodeMirror').each(function(index, el) { $(el).removeClass('in-small-font in-large-font'); });
                    set_cookie('in.editor.option.fontSize','medium');
                    break;
            }
            in_editor.refresh();
        }
    }

    function word_count(cm) {
        var words = cm.getValue().match(/[\u00ff-\uffff]|\S+/g);
        var count = words ? words.length : 0;
        $('#in-word-count').html(count);
        if(count === 0) {
            $('#in-refresh-preview').attr('disabled', true);
            $('#in-save-txt').addClass('is-disabled');
        }else if(!$('#in-refresh-preview').hasClass('is-loading')) {
            $('#in-refresh-preview').attr('disabled', false);
            $('#in-save-txt').removeClass('is-disabled');
        }
        return count;
    }

    function set_preview_has_scene_num(el) {
        if(el.is(':checked')) {
            set_cookie('in.preview.option.hasSceneNum','true');
        }
        else {
            set_cookie('in.preview.option.hasSceneNum','false');
        }
    }

    function set_preview_strong_scene_heading(el) {
        if(el.is(':checked')) {
            set_cookie('in.preview.option.strongSceneHeading','true');
        }
        else {
            set_cookie('in.preview.option.strongSceneHeading','false');
        }
    }

    function set_preview_first_page_num(el) {
        if(el.is(':checked')) {
            set_cookie('in.preview.option.firstPageNum','true');
        }
        else {
            set_cookie('in.preview.option.firstPageNum','false');
        }
    }

    function set_local_storage(key, value) {
        var localStorage;
        try {
          localStorage = window.localStorage;
          localStorage.setItem(key + '.' + IN_LANG, value);
        } catch(e) {}
    }

    function get_local_storage(key) {
        var localStorage;
        try {
          localStorage = window.localStorage;
          return localStorage.getItem(key + '.' + IN_LANG);
        } catch(e) { return ''}
    }

    function set_cookie(key, value) {
        Cookies.set(key + '.' + IN_LANG, value);
    }

    function get_cookie(key) {
        return Cookies.get(key + '.' + IN_LANG);
    }
    
    function save_in_to_local_storage() {
        set_local_storage(LS_KEY_IN,in_editor.getValue());
    }

    function in_resize() {
        height_trunk = 50;
        $('#in-collaps-arrow').css({marginTop:$(window).height()/2-height_trunk+'px'});
        $('#in-preview-container').height($(window).height()-height_trunk-2);
        if($(window).width() < 768) {
            height_trunk += 100;
        }
        if (navigator.userAgent.match(/(iPhone|iPad|iPod)/) && IN_LANG === 'zh') {
            $(in_editor.getWrapperElement()).hide();
            $('#in-juben-text').height($(window).height()-height_trunk-12);
            $('#in-juben-text').attr('placeholder','');
            $('#in-juben-text').show();
        }
        $('.CodeMirror').each(function(index, el) { 
            $(el).height($(window).height()-height_trunk-2);
        });
        $('#in-preview-container').show();
        $('#in-collaps-arrow').show();
        $('#in-progress-bar-parent').height($('#in-preview-container').height());
        $('#in-progress-bar-parent').width($('#in-preview-container').width());
    }

    function submit_preview() {
        $('#in-refresh-preview').toggleClass('is-loading').attr('disabled', function(i, v) { return !v; });
        $('#in-preview-settings-menu').addClass('in-preview-settings-menu-loading');
        save_in_to_local_storage();
        $('#in-form').submit();
    }

    function after_render(is_successful) {
        if(is_successful === undefined) is_successful = true
        if($('#in-refresh-preview').hasClass('is-loading')) $('#in-refresh-preview').toggleClass('is-loading');
        if(!$('#in-preview-settings-menu').hasClass('in-preview-settings-menu')) $('#in-preview-settings-menu').addClass('in-preview-settings-menu');
        $('#in-preview-settings-menu').removeClass('in-preview-settings-menu-loading');
        if(is_successful) {
            $('#in-ec-pdf').removeClass('is-disabled');
            $('#in-save-pdf').attr('disabled', false);
        }else {
            $('#in-ec-pdf').addClass('is-disabled');
            $('#in-save-pdf').attr('disabled', true);
        }
        $('#in-preview-container').scrollTop(get_cookie('in.preview.state.scrollTop'));
        hide_progress_bar();
    }

    function render_pdf(pdf_container, pdf_raw_content, fade_in, div_scale) {
        if(fade_in === undefined) fade_in = true;
        if(div_scale === undefined) div_scale = 1;
        var pdf_content = atob(pdf_raw_content);
        var index = 0;
        var new_canvas;
        var context;
        show_progress_bar();
        pdfjsLib.getDocument({data:pdf_content}).promise.then(function (pdf) {
            var scale = 1;
            var div_width = 100*div_scale;
            var num_pages = pdf.numPages;
            $('.in-div-page-container').each(function(index, el){
                $(el).find('canvas').get(0).getContext('2d').clearRect(0, 0, $(el).find('canvas').attr('width'), $(el).find('canvas').attr('height'));
                $(el).find('canvas').attr('width', 0);
                $(el).find('canvas').attr('height', 0);
                $(el).empty();
            });
            pdf_container.empty();
            pdf.getPage(1).then(function(page) {
                scale = (pdf_container.width()/page.getViewport({scale:1}).width - 0.005)*div_scale;
            });
            for (var i = 1; i <= num_pages; i ++) {
                pdf.getPage(i).then(function(page) {
                    var viewport = page.getViewport({ scale: scale });
                    new_canvas = $('<canvas/>').prop({
                        width: viewport.width*PIXEL_RATIO,
                        height:  viewport.height*PIXEL_RATIO
                    });
                    context = new_canvas.get(0).getContext('2d');
                    if(PIXEL_RATIO > 1) new_canvas.width(viewport.width).height(viewport.height);
                    context.setTransform(PIXEL_RATIO, 0, 0, PIXEL_RATIO, 0, 0);
                    
                    var renderContext = {
                        canvasContext: context,
                        viewport: viewport
                    };
                    var renderTask = page.render(renderContext);
                        renderTask.promise.then(function () {
                        index ++;
                        if(index === num_pages) {
                            hide_progress_bar();
                            after_render();
                            refresh_count ++;
                        }
                     });
                    var child_div = $('<div class="in-div-page-container" style="width:' + div_width + '%" />');
                    child_div.append(new_canvas);
                    pdf_container.append(child_div);
                    context.clearRect(0, 0, new_canvas.width, new_canvas.height);
                    new_canvas = null;
                    context = null;
                });
            }
        }, function(reason) {console.error(reason)});
    }

    function show_progress_bar() {
        $('#in-progress-bar-parent').width($('#in-preview-container').width());
        $('#in-progress-bar').css({marginTop: ($('#in-progress-bar-parent').height()/2) - 50 +'px', marginLeft:($('#in-preview-container').width()-100)/2 + 'px'});
        $('#in-progress-bar-parent').removeClass('in-hidden').fadeIn('fast');
    }

    function hide_progress_bar() {
         $('#in-progress-bar-parent').fadeOut('fast').addClass('in-hidden');
    }

    function submit_form(form_obj, event) {
        event.preventDefault();
        var post_url = $(form_obj).attr('action');
        $('#in-juben-text').val(in_editor.getValue());
        var request_method = $(form_obj).attr('method');
        var form_data = $(form_obj).serialize();
       
        $.ajax({
            url: post_url,
            type: request_method,
            dataType: 'text',
            data: form_data,
            beforeSend: function(xhr) {
                show_progress_bar();
                $('#in-ec-pdf').addClass('is-disabled');
                if(refresh_count > 0) set_cookie('in.preview.state.scrollTop', $('#in-preview-container').scrollTop());
            }, 
            error: function(xhr) {
                alert(xhr.statusText + '\n' +  xhr.responseText);
                after_render(false);
            },
            success: function(response) {
                injuben_result = jQuery.parseJSON(response)
                render_pdf(pdf_container, injuben_result.content);
            }
        });
    }
});
