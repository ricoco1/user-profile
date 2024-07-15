const socket = io();
        
        socket.on('profile_update', function(data) {
            const profileGallery = document.querySelector('#profile-gallery');
            const newProfileCard = `
                <div class="col-sm-12 col-md-6 col-lg-4" id="profile-${data._id}">
                    <div class="card mb-4">
                        <div class="card-body profile-info">
                            <img src="static/uploads/img/${data.filename}" class="profile-img" alt="Profile Image">
                            <div class="details">
                                <h5 class="card-title">${data.name}</h5>
                                <p class="card-text">${data.phone}</p>
                                <p class="card-text">${data.email}</p>
                                <p class="card-text">${data.hobby}</p>
                                <a href="/edit/${data._id}" class="btn btn-warning">Edit</a>
                                <form action="/delete/${data._id}" method="POST" class="d-inline">
                                    <button class="btn btn-danger" type="submit">Delete</button>
                                </form>
                            </div>
                        </div>
                    </div>
                </div>`;
            profileGallery.innerHTML += newProfileCard;
        });
        
        socket.on('profile_delete', function(data) {
            const profileCard = document.querySelector(`#profile-${data.profile_id}`);
            profileCard.remove();
        });
        
        socket.on('profile_edit', function(data) {
            const profileCard = document.querySelector(`#profile-${data._id}`);
            profileCard.querySelector('.profile-img').src = `static/uploads/img/${data.filename}`;
            profileCard.querySelector('.card-title').textContent = data.name;
            profileCard.querySelector('.card-text:nth-of-type(1)').textContent = data.phone;
            profileCard.querySelector('.card-text:nth-of-type(2)').textContent = data.email;
            profileCard.querySelector('.card-text:nth-of-type(3)').textContent = data.hobby;
        });
