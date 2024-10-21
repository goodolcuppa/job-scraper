function checkUsername(e) {
    if (e.value.length < 2) {
        e.classList.remove('is-success');
        e.classList.add('is-danger');
    }
    else {
        e.classList.remove('is-danger');
        e.classList.add('is-success');
    }
}

function checkPassword(e) {
    if (e.value.length < 6) {
        e.classList.remove('is-success');
        e.classList.add('is-danger');
    }
    else {
        e.classList.remove('is-danger');
        e.classList.add('is-success');
    }
}

function checkConfirmPassword(e) {
    password = document.getElementById('password')
    if (!password.classList.contains('is-success') || e.value !== password.value) {
        e.classList.remove('is-success');
        e.classList.add('is-danger');
    }
    else {
        e.classList.remove('is-danger');
        e.classList.add('is-success');
    }
}

function saveJob(e, job) {
    e.classList.remove('is-outlined');
    e.setAttribute('disabled', true);

    fetch('save-job', {
        method: 'POST',
        body: JSON.stringify({job: job})
    });
}

function deleteJob(jobId) {
    fetch('/delete-job', {
        method: 'POST',
        body: JSON.stringify({ jobId: jobId })
    }).then((_res) => {
        window.location.href = '/saved';
    });
}