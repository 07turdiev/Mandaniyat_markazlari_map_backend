window.addEventListener('load', function () {
    setTimeout(function () {
        console.log('[CASCADE] Script ishga tushdi');

        var jq = window.django && window.django.jQuery;
        if (!jq) {
            console.error('[CASCADE] django.jQuery topilmadi!');
            return;
        }

        // Select2 ni olib tashlash
        ['#id_region', '#id_district', '#id_mahalla'].forEach(function (sel) {
            var $el = jq(sel);
            if ($el.data('select2')) {
                $el.select2('destroy');
                console.log('[CASCADE] Select2 olib tashlandi:', sel);
            }
        });

        var region = document.getElementById('id_region');
        var district = document.getElementById('id_district');
        var mahalla = document.getElementById('id_mahalla');

        console.log('[CASCADE] region:', !!region, 'district:', !!district, 'mahalla:', !!mahalla);
        console.log('[CASCADE] DISTRICTS_BY_REGION:', typeof window.DISTRICTS_BY_REGION, window.DISTRICTS_BY_REGION ? Object.keys(window.DISTRICTS_BY_REGION).length + ' viloyat' : 'YO\'Q');
        console.log('[CASCADE] MAHALLAS_BY_DISTRICT:', typeof window.MAHALLAS_BY_DISTRICT, window.MAHALLAS_BY_DISTRICT ? Object.keys(window.MAHALLAS_BY_DISTRICT).length + ' tuman' : 'YO\'Q');

        if (!region || !district) {
            console.error('[CASCADE] region yoki district elementi topilmadi!');
            return;
        }

        var districtsByRegion = window.DISTRICTS_BY_REGION || {};
        var mahallasByDistrict = window.MAHALLAS_BY_DISTRICT || {};

        var savedDistrict = district.value;
        var savedMahalla = mahalla ? mahalla.value : '';

        function fillSelect(sel, items, saved, placeholder) {
            sel.innerHTML = '';
            var def = document.createElement('option');
            def.value = '';
            def.textContent = placeholder;
            sel.appendChild(def);

            (items || []).forEach(function (item) {
                var opt = document.createElement('option');
                opt.value = item.id;
                opt.textContent = item.name;
                if (String(item.id) === String(saved)) opt.selected = true;
                sel.appendChild(opt);
            });
            console.log('[CASCADE] fillSelect:', sel.id, items ? items.length : 0, 'ta element');
        }

        function onRegionChange() {
            var rid = region.value;
            console.log('[CASCADE] Viloyat tanlandi: id=' + rid);
            var items = districtsByRegion[rid] || [];
            console.log('[CASCADE] Tumanlar soni:', items.length);
            fillSelect(district, items, savedDistrict, '-- Tumanni tanlang --');
            if (mahalla) fillSelect(mahalla, [], '', '-- Avval tuman tanlang --');
            if (district.value) onDistrictChange();
        }

        function onDistrictChange() {
            if (!mahalla) return;
            var did = district.value;
            console.log('[CASCADE] Tuman tanlandi: id=' + did);
            var items = mahallasByDistrict[did] || [];
            console.log('[CASCADE] Mahallalar soni:', items.length);
            fillSelect(mahalla, items, savedMahalla, '-- Mahallani tanlang --');
        }

        region.addEventListener('change', function () {
            console.log('[CASCADE] region change EVENT ishladi');
            savedDistrict = '';
            savedMahalla = '';
            onRegionChange();
        });

        district.addEventListener('change', function () {
            console.log('[CASCADE] district change EVENT ishladi');
            savedMahalla = '';
            onDistrictChange();
        });

        if (region.value) {
            onRegionChange();
        }

        console.log('[CASCADE] Tayyor!');
    }, 500);
});
