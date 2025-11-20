const utils = {
    // Render a list of objects into a table body
    renderTable: (tbodyId, data, columns) => {
        const tbody = document.getElementById(tbodyId);
        if (!tbody) return;

        tbody.innerHTML = ''; // Clear existing rows

        if (!data || data.length === 0) {
            tbody.innerHTML = `<tr><td colspan="${columns.length + 1}" class="text-center">No records found</td></tr>`;
            return;
        }

        data.forEach(item => {
            const tr = document.createElement('tr');
            columns.forEach(colKey => {
                const td = document.createElement('td');
                td.textContent = item[colKey] || '-'; 
                tr.appendChild(td);
            });
            
            // Add Action Buttons
            const actionTd = document.createElement('td');
            actionTd.innerHTML = `
                <button class="btn btn-sm btn-primary" onclick="editItem('${item.id}')"><i class="fa-solid fa-pen"></i></button>
                <button class="btn btn-sm" style="background: var(--danger); color: white;" onclick="deleteItem('${item.id}')"><i class="fa-solid fa-trash"></i></button>
            `;
            tr.appendChild(actionTd);
            
            tbody.appendChild(tr);
        });
    }
};

// --- Global Action Handlers (Required for onclick events) ---

window.editItem = (id) => {
    let endpoint = '';
    if(location.href.includes('persons')) endpoint = '/persons';
    else if(location.href.includes('locations')) endpoint = '/locations';
    else if(location.href.includes('activities')) endpoint = '/activities';
    else if(location.href.includes('schools')) endpoint = '/schools';

    if(!endpoint) return;

    const newValue = prompt(`Edit item ${id}? Enter new Name/Description:`);
    if(newValue) {
        // We assume we are updating the main 'name' or 'description' field for simplicity
        await api.put(`${endpoint}/${id}`, { value: newValue });
        alert('Update successful');
        location.reload();
    }
};

window.deleteItem = async (id) => {
    if(confirm(`Are you sure you want to delete item ${id}?`)) {
        // Determine the context based on the URL to know which API endpoint to hit
        // This is a simple heuristic for your project
        let endpoint = '';
        if(location.href.includes('persons')) endpoint = '/persons';
        else if(location.href.includes('locations')) endpoint = '/locations';
        else if(location.href.includes('activities')) endpoint = '/activities';
        else if(location.href.includes('schools')) endpoint = '/schools';
        
        if(endpoint) {
            await api.post(`${endpoint}/delete`, { id: id }); // Or api.delete if you implement it
            alert('Item deleted');
            location.reload();
        } else {
            console.log('Delete logic not implemented for this page yet.');
        }
    }
};