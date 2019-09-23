// thanos.js

/*
知识点：

逻辑运算返回值：
1、只要“||”前面为false,不管“||”后面是true还是false，都返回“||”后面的值;
2、只要“||”前面为true,不管“||”后面是true还是false，都返回“||”前面的值;
3、只要“&&”前面是false，无论“&&”后面是true还是false，结果都将返“&&”前面的值;
4、只要“&&”前面是true，无论“&&”后面是true还是false，结果都将返“&&”后面的值。

正则直接量语法
/regexp/g 是g修饰符对全局匹配的直接量语法，等同于new RegExp("regexp","g")，以下为对正则表达式 "^\s+|\s+$" 进行全局搜索

按子元素的属性在jq的dom中查找
$xx.find('button[type=submit]')，表示，在xx元素中，查找子元素为button且其type属性为submit的目标。

*/

if (! window.console) {
	window.console = {
		log: function() {},
		info: function() {},
		error: function() {},
		warn: function() {},
		debug: function() {}
	};
}

if (! String.prototype.trim) {
	String.prototype.trim = function() {
		return this.replace(/^\s+|\s+$/g, '');
	};
}

if (! Number.prototype.toDateTime) {
	var replaces = {
		'yyyy': function(dt) {
			return dt.getFullYear().toString();
		},
		'yy': function(dt) {
			return (dt.getFullYear() % 100).toString();
		},
		'MM': function(dt) {
			var m = dt.getMonth() + 1;
			return m < 10 ? '0' + m : m.toString();
		},
		'M': function(dt) {
			var m = dt.getMonth() + 1;
			return m.toString();
		},
		'dd': function(dt) {
			var d = dt.getDate();
			return d < 10 ? '0' + d : d.toString();
		},
		'd': function(dt) {
			var d = dt.getDate();
			return d.toString();
		},
		'hh': function(dt) {
			var h = dt.getHours();
			return h < 10 ? '0' + h : h.toString();
		},
		'h': function(dt) {
			var h = dt.getHours();
			return h.toString();
		},
		'mm': function(dt) {
            var m = dt.getMinutes();
            return m < 10 ? '0' + m : m.toString();
        },
        'm': function(dt) {
            var m = dt.getMinutes();
            return m.toString();
        },
        'ss': function(dt) {
            var s = dt.getSeconds();
            return s < 10 ? '0' + s : s.toString();
        },
        's': function(dt) {
            var s = dt.getSeconds();
            return s.toString();
        },
        'a': function(dt) {
            var h = dt.getHours();
            return h < 12 ? 'AM' : 'PM';
        }
	};
	var token = /([a-zA-Z]+)/;
	Number.prototype.toDateTime = function(format) {
		var fmt = format || 'yyyy-MM-dd hh:mm:ss'
		var dt = new Date(this * 1000);
		var arr = fmt.split(token);
		for (var i=0; i<arr.length; i++) {
			var s = arr[i];
			if (s && s in replaces) {
				arr[i] = replaces[s](dt);
			}
		}
		return arr.join('');
	}
}

function encodeHtml(str) {
	return String(str)
		.replace(/&/g, '&amp;')
		.replace(/"/g, '&quot;')
		.replace(/'/g, '&#39;')
		.replace(/</g, '&lt;')
		.replace(/>/g, '&gt;');
}

function parseQueryString() {
	var q = location.search,
	r = {},
	i, pos, s, qs;
	if (q && q.charAt(0)==='?') {
		qs = q.substring(1).split('&');
		for (i=0; i<qs.length; i++) {
			s = qs[i];
			pos = s.indexOf('=');
			if (pos <= 0) {
				continue;
			}
			r[s.substring(0, pos)] = decodeURIComponent(s.substring(pos+1).replaces(/\+/g, ' '));
		}
	}
	return r;
}

function gotoPage(i) {
	var r = parseQueryString();
	r.page = i;
	location.assign('?' + $.param(r));
}

function refresh() {
	var t = new Date().getTime(),
	url = location.pathname;
	if (location.search) {
		url = url + location.search + '&t=' + t;
	}
	else {
		url = url + '?t=' + t;
	}
	location.assign(url);
}

function toSmartDate(timestamp) {
	if (typeof(timestamp)==='string') {
		timestamp = parseInt(timestamp);
	}
	if (isNan(timestamp)) {
		return '';
	}

	var today = new Date(g_time),
	    now = today.getTime(),
	    s = '1分钟前 ',
	    t = now - timestamp;
	if (t > 604800000) {
	    // 1 week ago;
	    var that = new Date(timestamp);
	    var y = that.getFullYear(),
	        m = that.getMonth() + 1,
	        d = that.getDate(),
	        hh = that.getHours(),
	        mm = that.getMinutes();
	    s = y === today.getFullYear() ? '' : y + '年';
	    s = s + m + '月' + d + '日' + hh + ':' + (mm < 10 ? '0' : '') + mm;
	}
	else if (t >= 86400000) {
	    // 1-6 days ago
	    s = Math.floor(t / 86400000) + '天前';
	}
	else if (t >= 3600000) {
	    // 1-23 hours ago
	    s = Math.floor(t / 3600000) + '小时前';
	}
	else if (t >= 60000) {
	    s = Math.floor(t / 60000) + '分钟前';
	}
	return s;
}

// 自执行匿名函数，遍历页面中的智能日期通配符，替换为智能日期
$(function() {
    $('.x-smartdate').each(function() {
        $(this).removeClass('x-smartdate').text(toSmartDate($(this).attr('date')));
    });
});

function Template(tpl) {
    var fn,
        match,
        code = ['var r=[];\nvar _html = function(str) { return str.replace(/&/g, \'&amp;\').replace(/"/g, \'&quot;\').replace(/\'/g, \'&#39;\').replace(/</g, \'&lt;\').replace(/>/g, \'&gt;\'); };'],
        re = /\{\s*([a-zA-Z\.\_0-9()]+)(\s*\|\s*safe)?\s*\}/m,
        addLine = function (text) {
            code.push('r.push(\''+text.replace(/\'/g, '\\\'').replace(/\n/g, '\\n').replace(/\r/g, '\\r')+'\');');
        };
    while (match = re.exec(tpl)) {
        if (match.index > 0) {
            addLine(tpl.slice(0, match.index));
        }
        if (match[2]) {
            code.push('r.push(String(this.' + match[1] + '));');
        }
        else {
            code.push('r.push(_html(String(this.' + match[1] + ')));');
        }
        tpl = tpl.substring(match.index + match[0].length);
    }
    addLine(tpl);
    code.push('return r.join(\'\');');
    fn = new Function(code.join('\n'));
    this.render = function (model) {
        return fn.apply(model);
    };
}

// extends jQuery.form:

$(function () {
    console.log('Extends $form...');
    $.fn.extend({
        showFormError: function (err) {
        	return this.each(function () {
        		var $form = $(this),
        			$alert = $form && $form.find('.uk-alert-danger'),
        			fieldName = err && err.data;
        		if (! $form.is('form')) {
        			console.error('Cannot call showFormError() on non-form object.');
        			return;
        		}
        		$form.find('input').removeClass('uk-form-danger');
        		$form.find('select').removeClass('uk-form-danger');
        		$form.find('textarea').removeClass('uk-form-danger');
        		if ($alert.length === 0) {
        			console.warn('Cannot find .uk-alert-danger element.');
        			return;
        		}

        		if (err) {
        			$alert.text(err.message ? err.message : (err.error ? err.error : err)).removeClass('uk-hidden').show();
        			if (($alert.offset().top - 60) < $(window).scrollTop()) {
        				$('html,body').animate({ scrollTop: $alert.offset().top - 60 });
        			}
        			if (fieldName) {
        				$form.find('[name=' + fieldName + ']').addClass('uk-form-danger');
        			}
        		}
        		else {
        			$alert.addClass('uk-hidden').hide();
        			$form.find('.uk-form-danger').removeClass('uk-form-danger');
        		}
        	});
        },
        showFormLoading: function (isLoading) {
        	return this.each(function () {
        		var $form = $(this),
        			$submit = $form && $form.find('button[type=submit]'),
        			$buttons = $form && $form.find('button');
        			$span = $submit && $submit.find('span');
        			// iconClass = $span && $span.attr('class');
        		// if (! $iconClass || iconClass.indexOf('uk-icon') < 0) {
        		// 	console.warn('Icon <i class="uk-icon>" not found.');
        		// 	return;
        		// }
        		if (isLoading) {
        			$buttons.attr('disabled', 'disabled');
        			$span && $span.removeAttr('uk-spinner');
        		}
        		else {
        			$buttons.removeClass('disabled');
        			$span && $span.removeAttr('uk-spinner');
        		}
        	});
        },
        postJSON: function(url, data, callback) {
        	if (arguments.length===2) {
        		callback = data;
        		data = {};
        	}
        	return this.each(function() {
        		var $form = $(this);
        		$form.showFormError();
        		$form.showFormLoading(true);
        		_httpJSON('POST', url, data, function(err, r) {
        			if (err) {
        				$form.showFormError(err);
        				$form.showFormLoading(false);
        			}
        			callback && callback(err, r);
        		});
        	});
        }
    });
});

function _httpJSON(method, url, data, callback) {
	var opt = {
		type: method,
		dataType: 'json'
	};
	if (method==='GET') {
		opt.url = url + '?' + data;
	}
	if (method==='POST') {
		opt.url = url;
		opt.data = JSON.stringify(data || {});
		opt.contentType = 'application/json';
	}
	$.ajax(opt).done(function (r) {
		if (r && r.error) {
			return callback(r);
		}
		return callback(null, r);
	}).fail(function (jqXHR, textStatus) {
		return callback({'error': 'http_bad_response', 'data': '' + jqXHR.status, 'message': '网络好像出问题了（HTTP'+jqXHR.status+')'});
	});
}

function getJSON(url, data, callback) {
	if (arguments.length === 2) {
		callback = data;
		data = {};
	}
	if (typeof(data)==='object') {
		var arr = [];
		$.each(data, function(k, v) {
			arr.push(k + '=' + encodeURIComponent(v));
		});
		data = arr.join('&');
	}
	_httpJSON('GET', url, data, callback)
}

function postJSON(url, data, callback) {
	if (arguments.length === 2) {
		callback = data;
		data = {};
	}
	_httpJSON('POST', url, data, callback);
}

if (typeof(Vue)!=='undefined') {
	Vue.filter('datetime', function(value) {
		var d = value;
		if (typeof(value)==='number') {
			d = new Date(value);
		}
		return d.getFullYear() + '-' + (d.getMonth() + 1) + '-' + d.getDate() + ' ' + d.getHours() + ':' + d.getMinutes();
	});
	Vue.component('pagination', {
		template:'<ul class="uk-pagination">' +
                '<li v-if="! has_previous" class="uk-disabled"><span class="uk-icon" uk-icon="chevron-double-left"></span></li>' +
                '<li v-if="has_previous"><a v-attr="onclick:\'gotoPage(\' + (page_index-1) + \')\'" href="#0"><span class="uk-icon" uk-icon="chevron-double-left"></span></a></li>' +
                '<li class="uk-active"><span v-text="page_index"></span></li>' +
                '<li v-if="! has_next" class="uk-disabled"><span class="uk-icon" uk-icon="chevron-double-right"></span></li>' +
                '<li v-if="has_next"><a v-attr="onclick:\'gotoPage(\' + (page_index+1) + \')\'" href="#0"><span class="uk-icon" uk-icon="chevron-double-right"></span></a></li>' +
            '</ul>'
	});
}

function redirect(url) {
	var hash_pos = url.indexOf('#'),
		query_pos = url.indexOf('?'),
		hash = '';
	if (hash_pos >= 0) {
		hash = url.substring(hash_pos);
		url = url.substring(0, hash_pos);
	}
	url = url + (query_pos >= 0 ? '&' : '?') + 't=' + new Date().getTime() + hash;
	console.log('redirect to:' + url);
	location.assign(url);
}

function _bindSubmit($form) {
	$form.submit(function (event) {
		event.preventDefault();
		showFormError($form, null);
		var fn_error = $form.attr('fn-error'),
			fn_success = $form.attr('fn-success'),
			fn_data = $form.attr('fn-data'),
			data = fn_data ? window[fn_data]($form) : $form.serialize();
		var $submit = $form.find('button[type=submit]'),
			$span = $submit.find('span');
		// 	iconClass = $span.attr('class');
		// if (!iconClass || iconClass.indexOf('uk-icon') < 0) {
		// 	$span = undefined;
		// }
		$submit.attr('disabled', 'disabled');
		$span && $span.attr('uk-spinner');
		postJSON($form.attr('action-url'), data, function (err, result) {
			$span && $span.removeAttr('uk-spinner');
            if (err) {
                console.log('postJSON failed: ' + JSON.stringify(err));
                $submit.removeAttr('disabled');
                fn_error ? fn_error() : showFormError($form, err);
            }
            else {
                var r = fn_success ? window[fn_success](result) : false;
                if (r===false) {
                    $submit.removeAttr('disabled');
                }
            }
		});
	});
	$form.find('button[type=submit]').removeAttr('disabled');
}

$(function () {
    $('form').each(function () {
        var $form = $(this);
        if ($form.attr('action-url')) {
            _bindSubmit($form);
        }
    });
});

$(function() {
    if (location.pathname === '/' || location.pathname.indexOf('/blog')===0) {
        $('li[data-url=blogs]').addClass('uk-active');
    }
});

function _display_error($obj, err) {
    if ($obj.is(':visible')) {
        $obj.hide();
    }
    var msg = err.message || String(err);
    var L = ['<div class="uk-alert uk-alert-danger">'];
    L.push('<p>Error: ');
    L.push(msg);
    L.push('</p><p>Code: ');
    L.push(err.error || '500');
    L.push('</p></div>');
    $obj.html(L.join('')).slideDown();
}

function error(err) {
    _display_error($('#error'), err);
}

function fatal(err) {
    _display_error($('#loading'), err);
}

