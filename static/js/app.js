document.addEventListener('DOMContentLoaded', function() {
    // CSRF token helper for AJAX
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    window.csrfToken = getCookie('csrftoken');

    // Auto-calculate diesel amount = litres * rate
    const dieselLitres = document.getElementById('id_diesel_litres');
    const dieselRate = document.getElementById('id_diesel_rate');
    const dieselAmount = document.getElementById('id_diesel_amount');

    function calcDiesel() {
        if (dieselLitres && dieselRate && dieselAmount) {
            const litres = parseFloat(dieselLitres.value) || 0;
            const rate = parseFloat(dieselRate.value) || 0;
            dieselAmount.value = (litres * rate).toFixed(2);
        }
    }

    if (dieselLitres) dieselLitres.addEventListener('input', calcDiesel);
    if (dieselRate) dieselRate.addEventListener('input', calcDiesel);

    // Customer search autocomplete
    const custInput = document.getElementById('id_customer_search');
    const custIdField = document.getElementById('id_customer');
    const custDropdown = document.getElementById('customer-dropdown');

    if (custInput && custDropdown) {
        let debounceTimer;
        custInput.addEventListener('input', function() {
            clearTimeout(debounceTimer);
            const query = this.value.trim();
            if (query.length < 2) {
                custDropdown.innerHTML = '';
                custDropdown.classList.add('d-none');
                return;
            }
            debounceTimer = setTimeout(function() {
                fetch('/jobs/api/customer-search/?q=' + encodeURIComponent(query))
                    .then(r => r.json())
                    .then(data => {
                        custDropdown.innerHTML = '';
                        if (data.results && data.results.length > 0) {
                            data.results.forEach(function(c) {
                                const item = document.createElement('a');
                                item.href = '#';
                                item.className = 'dropdown-item';
                                item.textContent = c.name;
                                item.addEventListener('click', function(e) {
                                    e.preventDefault();
                                    custInput.value = c.name;
                                    custIdField.value = c.id;
                                    custDropdown.classList.add('d-none');
                                });
                                custDropdown.appendChild(item);
                            });
                            custDropdown.classList.remove('d-none');
                        } else {
                            custDropdown.classList.add('d-none');
                        }
                    });
            }, 300);
        });
    }

    // Driver auto-fetch from mobile number
    const driverMobile = document.getElementById('id_driver_mobile_no');
    const driverName = document.getElementById('id_driver_name');
    const driverDL = document.getElementById('id_dl_no');

    if (driverMobile) {
        driverMobile.addEventListener('blur', function() {
            const mobile = this.value.trim();
            if (mobile.length >= 10) {
                fetch('/operations/api/driver-by-mobile/?mobile=' + encodeURIComponent(mobile))
                    .then(r => r.json())
                    .then(data => {
                        if (data.found) {
                            if (driverName) driverName.value = data.name;
                            if (driverDL) driverDL.value = data.dl_no;
                        }
                    });
            }
        });
    }

    // Vehicles filtered by vendor (chained dropdown)
    const vendorSelect = document.getElementById('id_vendor');
    const vehicleSelect = document.getElementById('id_vehicle');

    if (vendorSelect && vehicleSelect) {
        vendorSelect.addEventListener('change', function() {
            const vendorId = this.value;
            if (!vendorId) {
                vehicleSelect.innerHTML = '<option value="">----Select----</option>';
                return;
            }
            fetch('/operations/api/vehicles-by-vendor/' + vendorId + '/')
                .then(r => r.json())
                .then(data => {
                    vehicleSelect.innerHTML = '<option value="">----Select----</option>';
                    data.vehicles.forEach(function(v) {
                        const opt = document.createElement('option');
                        opt.value = v.id;
                        opt.textContent = v.vehicle_no;
                        vehicleSelect.appendChild(opt);
                    });
                });
        });
    }
});
