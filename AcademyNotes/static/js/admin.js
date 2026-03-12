// Modals

function createModalItem(nameItem, itemId, nameObject, numDivsItems, listItemsDivs) {
    const modal = document.createElement('div');
    modal.className = 'modal';
    modal.id = `modal-item-${nameObject}-${itemId}`;
    const modalBackDrop = document.createElement('div');
    modalBackDrop.className = 'backdrop';
    const modalContent = document.createElement('div');
    modalContent.className = 'content';
    const modalHeader = document.createElement('div');
    modalHeader.className = 'header';
    const modalBody = document.createElement('div');
    modalBody.className = 'body';
    let divItems;
    let listItems;
    if (numDivsItems > 1) {
        listItemsDivs.forEach(item => {
            //console.log(item)
            divItems = document.createElement('div'); 
            divItems.dataset.class = `div-item-${item.itemName}-${item.objectName}`;
            modalBody.appendChild(divItems);
            listItems = document.createElement('ol');
            listItems.id = `modal-list-item-${item.itemName}-${item.objectName}`;
            divItems.appendChild(listItems);
        })
    } else {
        divItems = document.createElement('div');
        divItems.dataset.class = `div-item-${nameItem}-${nameObject}`;
        listItems = document.createElement('ol');
        listItems.id = `modal-list-item-${nameItem}-${nameObject}`;
    }
    const divButtons = document.createElement('div');
    divButtons.className = 'buttons-modal';
    const btnClose = document.createElement('button');
    btnClose.className = 'button';
    btnClose.id = `button-close-${nameItem}-${nameObject}`;
    btnClose.textContent = 'Cerrar';
    modal.appendChild(modalBackDrop);
    modalBackDrop.appendChild(modalContent);
    modalContent.appendChild(modalHeader);
    modalContent.appendChild(modalBody);
    modalBody.appendChild(divItems);
    divItems.appendChild(listItems);
    modalBody.appendChild(divButtons);
    divButtons.appendChild(btnClose);
    return modal;
};
// General generation
async function loadSubItemsList(data, datasetDivItemIdForObject, itemId, nameSubItem, nameItem, selectedGlobalSubItemIds, isSelectedForObject, datasetSubItemId, subItemDataset = '', SpSubItem, SpItem, oneOption = false, clearList = true, subSubItemsLoad=false, subSubItemName) {
    const subItems = data || [];
    try {
        subItems.sort((a, b) => a.name - b.name);
    } catch (err) {
        console.log('error: ', (err));
    }
    //console.log(datasetDivItemIdForObject)
    let divSubItem = document.querySelector(`div[${datasetDivItemIdForObject}="${itemId}"]`) 
    if (!divSubItem) {
        divSubItem = document.querySelector(`#list-${nameSubItem}-${nameItem}`);
    } 
    //console.log(divSubItem);
    
    if (divSubItem.dataset.loaded) {
        //divSubItem.innerHTML = '';
        return
    }
    if (true) {    
        //console.log(subItems);
        nameLabel = document.createElement('label');
        nameLabel.className = `name-label`;
        nameLabel.id = `name-label-${nameSubItem}-${SpItem}`;
        nameLabel.textContent = `Lista de ${SpSubItem}`;
        nameLabel.classList.add('show');
        if (!subItems || subItems.length == 0) {
            nameLabel.classList.remove('show');
            return;
        }
        divSubItem.appendChild(nameLabel);
    }

    if (divSubItem) {
        subItems.forEach(subItem => {
            // si un grado ya esta seleccionado antes de generarlo
            if (selectedGlobalSubItemIds.has(String(subItem.id))) {
                //console.log('comido')
                const label = document.createElement('label');
                label.textContent = subItem.name;
                label.dataset[`${nameSubItem}Id`] = subItem.id;
                label.dataset[`${nameItem}Id`] = itemId;
                label.className = `label-sub-item`;
                label.dataset[isSelectedForObject] = 'false';
                label.classList.add('hide');
                label.addEventListener('click', () => {
                    if (label.dataset[isSelectedForObject] == 'false') {
                        label.dataset[isSelectedForObject] = 'true';
                        label.classList.add('selected'); // para los estilos al sleccionar

                        selectedGlobalSubItemIds.add(String(subItem.id));

                        document.querySelectorAll(`label[${datasetSubItemId}="${subItem.id}"]`)
                            .forEach(l => { if (l !== label) l.classList.add('hide'); });

                    } else {
                        label.dataset[isSelectedForObject] = 'false';
                        label.classList.remove('selected');
                        selectedGlobalSubItemIds.delete(String(subItem.id));
                        document.querySelectorAll(`label[${datasetSubItemId}="${subItem.id}"]`)
                            .forEach(l => { if (l !== label) l.classList.remove('hide'); });
                    }
                });
                divSubItem.appendChild(label);            
                return;
            }

            // Genera el grado si no se ha seleccionado 
            const label = document.createElement('label');    
            label.textContent = subItem.name
            label.dataset[`${nameSubItem}Id`] = subItem.id;
            label.dataset[`${nameItem}Id`] = itemId;
            label.className = `label-sub-item`;
            label.dataset[isSelectedForObject] = 'false';
            label.addEventListener('click', () => {
                const divSubSubItem = divSubItem.querySelector('.div-sub-sub-item');
                if (subSubItemsLoad) {
                    if (label.dataset[isSelectedForObject] == 'false') {
                            label.dataset[isSelectedForObject] = 'true';
                            label.classList.add('selected'); // para los estilos al sleccionar
                            //console.log(label)

                            // selectedGlobalSubItemIds.add(String(subItem.id));
                            
                            //selectedGlobalSubItemIds.add(String(subItem.id));

                            if (divSubSubItem.classList.contains('hide')) {
                                divSubSubItem.dataset[subItemDataset] = label.dataset[subItemDataset]
                                // divSubSubItem.textContent = label.dataset[subItemDataset];
                                divSubSubItem.classList.remove('hide');
                            } else {
                                divSubSubItem.dataset[subItemDataset] = label.dataset[subItemDataset]
                                // divSubSubItem.textContent = label.dataset[subItemDataset]; 
                            }


                            divSubItem.querySelectorAll(`.label-sub-item`)
                                .forEach(l => { 
                                    if (l !== label) {
                                        l.classList.remove('selected');
                                        l.dataset[isSelectedForObject] = 'false';
                                } 
                            });
                    } else {
                        label.dataset[isSelectedForObject] = 'false';
                        label.classList.remove('selected');

                        divSubSubItem.classList.add('hide')   

                        //selectedGlobalSubItemIds.delete(String(subItem.id));

                        //divSubItem.querySelectorAll(`.label-sub-item`)
                            //.forEach(l => { if (l !== label) l.classList.add('selected');});
                    }
                } else {
                    if (label.dataset[isSelectedForObject] == 'false') {
                        label.dataset[isSelectedForObject] = 'true';
                        label.classList.add('selected'); // para los estilos al sleccionar

                        // selectedGlobalSubItemIds.add(String(subItem.id));
                        selectedGlobalSubItemIds.add(String(subItem.id));


                        if (oneOption) {
                            document.querySelectorAll(`.label-sub-item`)
                            .forEach(l => { if (l !== label) l.classList.add('hide'); });
                        } 
                        document.querySelectorAll(`label[${datasetSubItemId}="${subItem.id}"]`)
                            .forEach(l => { if (l !== label) l.classList.add('hide'); });
                    } else {
                        label.dataset[isSelectedForObject] = 'false';
                        label.classList.remove('selected');

                        selectedGlobalSubItemIds.delete(String(subItem.id));

                        if (oneOption) {
                            document.querySelectorAll(`.label-sub-item`)
                            .forEach(l => { if (l !== label) l.classList.remove('hide'); });
                        } 
                        document.querySelectorAll(`label[${datasetSubItemId}="${subItem.id}"]`)
                            .forEach(l => { if (l !== label) l.classList.remove('hide'); });
                    }
                }
            });
            divSubItem.appendChild(label);
            divSubItem.dataset.loaded = 'true';
        });
        if (subSubItemsLoad) {
            const divSubSubItem = document.createElement('div');
            divSubSubItem.className = `div-sub-sub-item`;
            divSubSubItem.classList.add('hide');
            const buttonAddSubSubItem = document.createElement('button');
            const buttonDeleteSubSubItem = document.createElement('button');
            const buttonEditSubSubItem = document.createElement('button');
            const divButtons = document.createElement('div');
            divButtons.className = 'buttons-modal';
            buttonAddSubSubItem.className = 'button-modal';
            buttonDeleteSubSubItem.className = 'button-modal';
            buttonEditSubSubItem.className = 'button-modal';
            buttonAddSubSubItem.textContent = `añadir ${SpSubItem}`;
            buttonEditSubSubItem.textContent = `Editar`;
            buttonDeleteSubSubItem.textContent = `Eliminar`;
            divSubItem.appendChild(divSubSubItem);
            divSubSubItem.appendChild(divButtons);
            divButtons.appendChild(buttonAddSubSubItem);
            divButtons.appendChild(buttonEditSubSubItem);
            divButtons.appendChild(buttonDeleteSubSubItem);
        }
    };
};
async function loadItemsList(dataItem, nameObject, nameItem, dataSubItems, datasetDivItemId, nameSubItem, selectedGlobalSubItemIds, isSelectedForObject, datasetSubItemId, subItemDataset, loadSubItems = true, SpItem, SpSubItem, oneOption = false, clearList = true, itemsModal = false, subSubItemsLoad=false) {
    const items = dataItem || [];
    //console.log(items, "items");
    try {
        items.sort((a, b) => a.name - b.name);
    } catch (err) {
        console.log('error: ', (err));
    }

    
    const list = itemsModal ? document.getElementById(`modal-list-item-${nameItem}-${nameObject}`) : document.getElementById(`list-${nameItem}-${nameObject}`);
    const itemsDOM = list.querySelector('.li');
    let nameLabel = document.getElementById(`name-label-${nameItem}-${nameObject}`);
    // console.log(itemsDOM, 'list', list);
    if (itemsDOM && clearList) {
        //list.innerHTML = '';
        return;
    }
    //console.log(nameLabel);
    if (!nameLabel) {    
        nameLabel = document.createElement('label');
        nameLabel.className = `name-label`;
        nameLabel.id = `name-label-${nameItem}-${nameObject}`;
        nameLabel.textContent = `Lista de ${SpItem}`;
        nameLabel.classList.add('show');
        if (!items || items.length == 0) {
            nameLabel.classList.remove('show');
            return;
        }
        list.appendChild(nameLabel);
    }
    items.forEach(item => {
        const li = document.createElement('li')
        li.textContent = item.name;
        li.className = 'li';
        li.dataset[`${nameItem}Id`] = item.id;
        list.appendChild(li)
//        console.log(li, "li");
        if (loadSubItems) {
            const divSubItem = document.createElement('div');
            divSubItem.dataset.class = `div-list`;
            divSubItem.className = `div-${nameSubItem}`;
            divSubItem.dataset[`${nameItem}IdFor${nameObject.charAt(0).toUpperCase() + nameObject.slice(1)}`] = item.id;
            list.appendChild(divSubItem);   
            li.addEventListener('click', (e) => {
                if (divSubItem.classList.contains('revelar')) {
                    divSubItem.dataset.loaded = 'false';
                    divSubItem.classList.remove('revelar');
                    //divSubItem.innerHTML = '';
                } else {
                    divSubItem.classList.add('revelar');
                    //loadSubItemsList(e = subItems, 'data-div-teacher-id', teacher.id_teacher, 'grade', 'teacher', selectedGradesIds, 'isSelectedForAsignature', 'data-grade-id').then(() => { div.dataset.loaded = 'true'; });
                    loadSubItemsList(e = dataSubItems, datasetDivItemId, item.id, nameSubItem, nameItem, selectedGlobalSubItemIds, isSelectedForObject, datasetSubItemId, subItemDataset, SpSubItem, SpItem, oneOption, clearList, subSubItemsLoad);
                    //loadGradesForTeacher(e = teacher.id_teacher).then(() => { div.dataset.loaded = 'true'; });
                }
            });
        } else {
        li.addEventListener('click', () => {
            if (li.dataset.isSelectedForGrade == "false") {
                li.dataset.isSelectedForGrade = 'true';
                li.classList.add('selected');
            } else {
                li.dataset.isSelectedForGrade = 'false';
                li.classList.remove('selected');
            }
        });
 //   });
        }
    });
};

// Load items

async function loadAsigGradesForActuallyTeacher() {
    try {
        const response = await fetch('http://127.0.0.1:5000/api/actually_teacher_asignatures', {
            method: 'GET',
            headers: { 'Accept': 'application/json' },
            credentials: 'include'
        });
        if (!response.ok) {
            throw new Error('Network response was not ok');
        };
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error loading grades:', error);
        return [];
    }
};

async function loadGrades() {
    try {
        const response = await fetch('http://127.0.0.1:5000/api/grades', {
            method: 'GET',
            headers: { 'Accept': 'application/json' },
            credentials: 'include'
        });
        if (!response.ok) {
            throw new Error('Network response was not ok');
        };
        const data = await response.json();
        return data.grades;
    } catch (error) {
        console.error('Error loading grades:', error);
        return [];
    }
};

async function loadTeachers() {
    try {
        const response = await fetch('http://127.0.0.1:5000/api/admin/teachers', {
            method: 'GET',
            headers: { 'Accept': 'application/json' },
            credentials: 'include'
        });
        if (!response.ok) {
            throw new Error('Network response was not ok');
        };
        const data = await response.json();
        return data.teachers;
    } catch (error) {
        console.error('Error loading asignatures:', error);
        return;
    }
};

async function loadAsignatures() {
    try {
        const response = await fetch('http://127.0.0.1:5000/api/asignatures', {
            method: 'GET',
            headers: { 'Accept': 'application/json' },
            credentials: 'include'
        });
        if (!response.ok) {
            throw new Error('Network response was not ok');
        };
        const data = await response.json();
        return data.asignatures;
    } catch (error) {
        console.error('Error loading grades:', error);
        return [];
    }
};

async function loadStudentsUndergraduate() {
    try {
        const response = await fetch('http://127.0.0.1:5000/api/students_undergraduate', {
            method: 'GET',
            headers: { 'Accept': 'application/json' },
            credentials: 'include'
        });
        if (!response.ok) {
            throw new Error('Network response was not ok');
        };
        const data = await response.json();
        const students = data.students || [];
        console.log(students)
        return students;
    } catch (error) {
        console.error('Error loading asignatures:', error);
        return;
    }
};

async function loadAsigGradesForNewTeacher() {
    try {
        const response = await fetch('http://127.0.0.1:5000/api/new_teacher_asignatures', {
            method: 'GET',
            headers: { 'Accept': 'application/json' },
            credentials: 'include'
        });
        if (!response.ok) {
            throw new Error('Network response was not ok');
        };
        const data = await response.json();
        // data.forEach(asignatura => {
        //     console.log(asignatura.nombre_asignatura);

        //     asignatura.grados.forEach(grado => {
        //         console.log(" - " + grado.grado_nombre);
        //     });
        // });
        const asignatures = data.asignatures || [];
        return data;
    } catch (error) {
        console.error('Error loading grades:', error);
        return [];
    }
};

const topBar = document.getElementById("barMenu");
const selectedGradesIds = new Set();
const selectedAsignatureIds = new Set();
addEventListener("scroll", function () {
    if (window.scrollY > 0) {
        topBar.classList.add("barMenu-scroll");
        topBar.style.position = "fixed";
    } else if (window.scrollY == 0) {
        topBar.classList.remove("barMenu-scroll");
        topBar.style.position = "static";
    }
});

// user logica
const btnOpenAddUSerModal = document.getElementById('button-add-user');
const btnCloseUserModal = document.getElementById('close-modal-user');
const btnSaveUSer = document.getElementById('save-user');
const modalUser = document.querySelector('#modal-user');

async function saveUser(name, password, role, institution) {
    try {
        const response = await fetch('http://127.0.0.1:5000/add_user_js', {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            credentials: 'include',
            body: JSON.stringify({
                name: name,
                password: password,
                role: role,
                institution: institution
            })
        });
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        const data = await response.json();
        console.log('User saved:', data);
        return data.id;
    } catch (error) {
        console.error('Error saving user:', error);
    }
};

async function loadCardListUsers(addEvent = true) {
    const UsersList = document.getElementById("users-list");
    try {
        const response = await fetch('http://127.0.0.1:5000/api/users/admin', {
            method: 'GET',
            headers: { 'Accept': 'application/json' },
            credentials: 'include'
        });
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        const data = await response.json();
        const users = data.users;
        const counter = document.getElementById("users-count");
        const btnShowMoreSubjects = document.getElementById('btn-show-more-users');
        if (users.length <= 4) {
            btnShowMoreSubjects.classList.add('hide');
        } else {
            btnShowMoreSubjects.classList.remove('hide');
        }
        if (addEvent) {
            btnShowMoreSubjects.addEventListener('click', () => {
                const hideItems = document.querySelectorAll('li[data-hide-user="true"]');
                if (btnShowMoreSubjects.dataset.hide == 'false') {
                    btnShowMoreSubjects.textContent = 'Ver menos usuarios.'
                    btnShowMoreSubjects.dataset.hide = 'true'
                    hideItems.forEach(item => {
                        item.dataset.hideUser = 'false';
                        item.classList.remove('hide');
                    });
                } else {
                    const hideItems = document.querySelectorAll('li[data-list-class="user-item"]');
                    btnShowMoreSubjects.textContent = 'Ver todas los usuarios...'
                    btnShowMoreSubjects.dataset.hide = 'false'
                    hideItems.forEach((item, idx) => {
                        if (idx + 2 > 5) {
                            item.dataset.hideUser = 'true';
                            item.classList.add('hide');
                        }
                    });
                }
            });
        }

        counter.textContent = `Total de usuarios: ${users.length}`;
        UsersList.innerHTML = '';
        users.forEach((user, idx) => {
            const li = document.createElement('li');
            li.textContent = user.username + ' - ' + user.role;
            li.dataset.teacherId = user.id_user;
            li.dataset.hideUser = 'false';
            li.dataset.listClass = 'user-item';
            li.className = 'li';
            li.dataset.number = idx + 1;
            if (li.dataset.number >= 5) {
                li.classList.add('hide');
                li.dataset.hideUser = 'true';
            }
            UsersList.appendChild(li);
        });
    } catch (error) {
        console.error('Error loading teachers:', error);
        return;
    }
};

// teacher logica
async function loadCardListTeacher(addEvent = true) {
    const teacherList = document.getElementById("teachers");
    try {
        const response = await fetch('http://127.0.0.1:5000/api/admin/teachers', {
            method: 'GET',
            headers: { 'Accept': 'application/json' },
            credentials: 'include'
        });
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        const data = await response.json();
        const teachers = data.teachers;
        const counter = document.getElementById("teachers-count");
        const btnShowMoreSubjects = document.getElementById('btn-show-more-teachers');
        if (teachers.length <= 4) {
            btnShowMoreSubjects.classList.add('hide');
        } else {
            btnShowMoreSubjects.classList.remove('hide');
        }
        if (addEvent) {
            btnShowMoreSubjects.addEventListener('click', () => {
                const hideItems = document.querySelectorAll('li[data-hide-teacher="true"]');
                if (btnShowMoreSubjects.dataset.hide == 'false') {
                    btnShowMoreSubjects.textContent = 'Ver menos profesores.'
                    btnShowMoreSubjects.dataset.hide = 'true'
                    hideItems.forEach(item => {
                        item.dataset.hideTeacher = 'false';
                        item.classList.remove('hide');
                    });
                } else {
                    const hideItems = document.querySelectorAll('li[data-list-class="teacher-item"]');
                    btnShowMoreSubjects.textContent = 'Ver todas los profesores...'
                    btnShowMoreSubjects.dataset.hide = 'false'
                    hideItems.forEach((item, idx) => {
                        if (idx + 2 > 5) {
                            item.dataset.hideTeacher = 'true';
                            item.classList.add('hide');
                        }
                    });
                }
            });
        }

        counter.textContent = `Total de profesores: ${teachers.length}`;
        teacherList.innerHTML = '';
        teachers.forEach((teacher, idx) => {
            const li = document.createElement('li');
            li.textContent = teacher.name;
            li.dataset.teacherId = teacher.id;
            li.dataset.hideTeacher = 'false';
            li.dataset.listClass = 'teacher-item';
            li.className = 'li';
            li.dataset.number = idx + 1;
            if (li.dataset.number >= 5) {
                li.classList.add('hide');
                li.dataset.hideTeacher = 'true';
            }
            teacherList.appendChild(li);
        });
    } catch (error) {
        console.error('Error loading teachers:', error);
        return;
    }
};

async function addTeacher(userId) {
    try {
        const response = await fetch('http://127.0.0.1:5000/add_teacher_js', {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            credentials: 'include',
            body: JSON.stringify({
                id_user: userId
            })
        });
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        const data = await response.json();
        console.log('teacher saved:', data.id);
        return data.id;
    } catch (error) {
        console.error('Error saving user:', error);
    }
};

// student logica
async function loadCardListStudents(addEvent = true) {
    const studentsList = document.getElementById("students-list");
    try {
        const response = await fetch('http://127.0.0.1:5000/api/students/admin', {
            method: 'GET',
            headers: { 'Accept': 'application/json' },
            credentials: 'include'
        });
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        const data = await response.json();
        const students = data.students;
        const counter = document.getElementById("students-count");
        const btnShowMoreSubjects = document.getElementById('btn-show-more-student');
        if (students.length <= 4) {
            btnShowMoreSubjects.classList.add('hide');
        } else {
            btnShowMoreSubjects.classList.remove('hide');
        }
        if (addEvent) {
            btnShowMoreSubjects.addEventListener('click', () => {
                const hideItems = document.querySelectorAll('li[data-hide-student="true"]');
                if (btnShowMoreSubjects.dataset.hide == 'false') {
                    btnShowMoreSubjects.textContent = 'Ver menos estudiantes.'
                    btnShowMoreSubjects.dataset.hide = 'true'
                    hideItems.forEach(item => {
                        item.dataset.hideStudent = 'false';
                        item.classList.remove('hide');
                    });
                } else {
                    const hideItems = document.querySelectorAll('li[data-list-class="student-item"]');
                    console.log(hideItems);
                    btnShowMoreSubjects.textContent = 'Ver todas los estudiantes...';
                    btnShowMoreSubjects.dataset.hide = 'false';
                    hideItems.forEach((item, idx) => {
                        if (idx + 2 > 5) {
                            item.dataset.hideStudent = 'true';
                            item.classList.add('hide');
                        }
                    });
                }
            });
        }

        counter.textContent = `Total de estudiantes: ${students.length}`;
        studentsList.innerHTML = '';
        students.forEach((student, idx) => {
            const li = document.createElement('li');
            li.textContent = student.name;
            li.dataset.studentId = student.id;
            li.dataset.hideStudent = 'false';
            li.dataset.listClass = 'student-item';
            li.className = 'li';
            li.dataset.number = idx + 1;
            if (li.dataset.number >= 5) {
                li.classList.add('hide');
                li.dataset.hideStudent = 'true';
            }
            studentsList.appendChild(li);
        });
    } catch (error) {
        console.error('Error loading students:', error);
        return;
    }
};

async function addStudent(userId, gradeId) {
        try {
            const response = await fetch('http://127.0.0.1:5000/add_student_js', {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            credentials: 'include',
            body: JSON.stringify({
                id_user: userId,
                id_grade: gradeId
            })
        });
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        const data = await response.json();
        console.log('teacher saved:', data.id);
        return data.id;
    } catch (error) {
        console.error('Error saving user:', error);
    }
};

// grade logica
const btnOpenAddGradeModal = document.getElementById('button-add-grade');
const btnCloseGradeModal = document.getElementById('close-modal-grade');
const btnSaveGrade = document.getElementById('save-grade');
const modalGrade = document.querySelector('#modal-grade');

async function addGradeForStudent(gradeId, studentId) {
    const payload = { id_grade: gradeId, id_student: studentId };
    const res = await fetch('http://127.0.0.1:5000/add_grade_for_student', {
        method: 'POST', credentials: 'include', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload)
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.message || 'Error creando nota');
    return data;
};
async function createGrade(nameGrade) {
    const payload = { name: nameGrade };
    const res = await fetch('http://127.0.0.1:5000/add_grade_js', {
        method: 'POST', credentials: 'include', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload)
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.message || 'Error creando nota');
    return data;
};
function openGradeModal() {
    modalGrade.classList.add("revelar");
    loadStudentsUndergraduate();

};
function closeGradeModal() {
    modalGrade.classList.remove('revelar')
};
async function saveGrade() {
    modalGrade.classList.remove('revelar');

    const input = document.getElementById('input-grade');
    const studentsSelected = document.querySelectorAll(`li[data-is-selected-for-grade=true]`);
    const grade = await createGrade(input.value);
    const asignatureSelected = document.querySelectorAll(`label[data-is-selected-for-grade=true]`);
    if (studentsSelected) {
        studentsSelected.forEach(student => {
            addGradeForStudent(grade.id, student.dataset.undergraduatestudentId);
        });
    if (asignatureSelected) {
        asignatureSelected.forEach(asignature => {
            syncTeacherAsignatureAssignment(asignature.dataset.teacherId, asignature.dataset.asignatureId, grade.id);
        });
    }
    const divSubItems = document.querySelectorAll(".div-asignature");
    divSubItems.forEach(divSubItem => {
        divSubItem.classList.remove('revelar');
    });
    const listUndergraduateStudentGrade = document.getElementById(`list-undergraduatestudent-grade`);
    listUndergraduateStudentGrade.innerHTML = '';
    selectedAsignatureIds.clear();
    divSubItems.innerHTML = '';
    // console.log(selectedGradesIds, 'clear');
    input.value = '';
}



    await loadCardListGrades(addEvent = false);
};
async function loadCardListGrades(addEvent = true) {
    const gradesList = document.getElementById("grades-list");
    const grades = await loadGrades();
    try {
        grades.sort((a, b) => a.name - b.name);
    } catch (err) {
        console.log('orden alfabetico', (err));
    }
    const counter = document.getElementById("grades-count");
    const btnShowMoreGrades = document.getElementById('btn-show-more-grades');
    if (grades.length <= 4) {
        btnShowMoreGrades.classList.add('hide');
    } else {
        btnShowMoreGrades.classList.remove('hide');
    }
    if (addEvent) {
        btnShowMoreGrades.addEventListener('click', () => {
            const hideItems = document.querySelectorAll('li[data-hide-grade="true"]');
            if (btnShowMoreGrades.dataset.hide == 'false') {
                btnShowMoreGrades.textContent = 'Ver menos grados.'
                btnShowMoreGrades.dataset.hide = 'true'
                hideItems.forEach(item => {
                    item.dataset.hideGrade = 'false';
                    item.classList.remove('hide');
                });
            } else {
                const hideItems = document.querySelectorAll('li[data-list-class="grade-item"]');
                btnShowMoreGrades.textContent = 'Ver todas los grados...'
                btnShowMoreGrades.dataset.hide = 'false'
                hideItems.forEach((item, idx) => {
                    if (idx + 2 > 5) {
                        item.dataset.hideGrade = 'true';
                        item.classList.add('hide');
                    }
                });
            }
        });
    }

    counter.textContent = `Total de grados: ${grades.length}`;
    gradesList.innerHTML = '';
    grades.forEach((grade, idx) => {
        const li = document.createElement('li');
        li.textContent = grade.name;
        li.dataset.gradeId = grade.id;
        li.dataset.hideGrade = 'false';
        li.dataset.listClass = 'grade-item';
        li.className = 'li';
        li.dataset.number = idx + 1;
        if (li.dataset.number >= 5) {
            li.classList.add('hide');
            li.dataset.hideGrade = 'true';
        }
        gradesList.appendChild(li);
    });
};

// asignatura -logica
const btnOpenAddAsignatureModal = document.getElementById('button-add-asignature');
const btnCloseAsignatureModal = document.getElementById('close-modal-asignature');
const btnSaveAsignature = document.getElementById('save-asignature');
const modalAsignature = document.querySelector('#modal-asignature');

async function loadCardListAsignature(addEvent = true) {
    const asignatureList = document.getElementById("list-asignatures");
    try {
        const asignatures = await loadAsignatures();
        const counter = document.getElementById("asignature-count");
        const btnShowMoreAsignature = document.getElementById('btn-show-more-asignature');
        if (asignatures.length <= 4) {
            btnShowMoreAsignature.classList.add('hide');
        } else {
            btnShowMoreAsignature.classList.remove('hide');
        }
        if (addEvent) {
            btnShowMoreAsignature.addEventListener('click', () => {
                const hideItems = document.querySelectorAll('li[data-hide-asignature="true"]');
                if (btnShowMoreAsignature.dataset.hide == 'false') {
                    btnShowMoreAsignature.textContent = 'Ver menos asignaturas.'
                    btnShowMoreAsignature.dataset.hide = 'true'
                    hideItems.forEach(item => {
                        item.dataset.hideAsignature = 'false';
                        item.classList.remove('hide');
                    });
                } else {
                    const hideItems = document.querySelectorAll('li[data-list-class="asignature-item"]');
                    btnShowMoreAsignature.textContent = 'Ver todas las asignaturas...'
                    btnShowMoreAsignature.dataset.hide = 'false'
                    hideItems.forEach((item, idx) => {
                        if (idx + 2 > 5) {
                            item.dataset.hideAsignature = 'true';
                            item.classList.add('hide');
                        }
                    });
                }
            });
        }

        counter.textContent = `Total de asignaturas: ${asignatures.length}`;
        asignatureList.innerHTML = '';
        const teacher_grades = await loadAsigGradesForActuallyTeacher();
        const grades_list = await loadAsigGradesForNewTeacher();
        const teacherActually = await loadTeachers();
        //console.log(teacher_grades)
        asignatures.forEach(async (asignature, idx) => {
            const li = document.createElement('li');
            li.textContent = asignature.name;
            li.dataset.asignatureId = asignature.id;
            li.dataset.hideAsignature = 'false';
            li.dataset.listClass = 'asignature-item';
            li.className = 'li';
            li.dataset.number = idx + 1;
            if (li.dataset.number >= 5) {
                li.classList.add('hide');
                li.dataset.hideAsignature = 'true';
            }
            const modal = createModalItem('teacher', asignature.id, asignature.name, 2, [{'itemName': 'teacher', 'objectName': asignature.name}, {'itemName': 'teachers', 'objectName': asignature.name}]);
            asignatureList.appendChild(modal);
            asignatureList.addEventListener('click', async (e) => {
                if (e.target.dataset.asignatureId == asignature.id && !modal.classList.contains('revelar')) {
                    let grades_dic = [];
                    let teachers_dic = [];
                    let grades_without_asignature = [];
                    teacher_grades.forEach(asigTeacher => {
                        if (asigTeacher.id == e.target.dataset.asignatureId) {
                            //console.log(asigTeacher);   
                            asigTeacher.teachers.forEach(async teacher => {
                                    teacher.grades.forEach(grade => {
                                        grades_dic.push({'name': grade.name, 'id': grade.id});
                                        
                                    });
                                    grades_list.forEach(grade => {
                                        if (grade.name == asignature.name) {
                                            grades_without_asignature = grade.grades;
                                            //console.log(grades_whiout_asignature)
                                        }
                                    });
                                    teachers_dic.push({'name': teacher.name, 'id': teacher.id})
                                    //console.log(grades_whiout_asignature.length)
                                    if (grades_without_asignature.length > 0) {
                                        loadItemsList(teacherActually, asignature.name, 'teachers', grades_without_asignature, `data-teachers-id-for-${asignature.name}`, 'grades', selectedGradesIds, 'isSelectedForAsignature', 'data-grades-id', '', true, 'asignar materia a un profesores', 'grados para asignar', false, true, true, true, false);
                                    }
                                    loadItemsList(teachers_dic, asignature.name, 'teacher', grades_dic, `data-teacher-id-for-${asignature.name}`, 'grade', selectedGradesIds, 'isSelectedForAsignature', 'data-grade-id', 'gradeId', true, 'Profesores de esta asignatura', 'Grados de este profesor', false, false, true, true);
                                    grades_dic = [];
                                    teachers_dic = [];
                                    grades_without_asignature = [];
                            });
                        }
                    });
                    modal.classList.add('revelar');
                    modal.querySelector('.header').innerHTML = `<h2> Asignatura: ${asignature.name} </h2>`;

                    modal.querySelector(`#button-close-teacher-${asignature.name}`).addEventListener('click', () => {
                        modal.classList.remove('revelar');
                        modal.querySelector(`#modal-list-item-teacher-${asignature.name}`).innerHTML = '';
                        selectedGradesIds.clear();
                    });
                }
            });
            asignatureList.appendChild(li);
        });
    } catch (error) {
        console.error('Error loading asignatures:', error);
        return;
    }
};

async function loadGradesForTeacher(teacherId) {
    try {
        const response = await fetch('http://127.0.0.1:5000/api/grades', {
            method: 'GET',
            headers: { 'Accept': 'application/json' },
            credentials: 'include'
        });
        if (!response.ok) {
            throw new Error('Network response was not ok');
        };
        const data = await response.json();
        const grades = data.grades || [];
        try {
            grades.sort((a, b) => a.name - b.name);
        } catch (err) {
            console.log('orden alfabetico', (err));
        }
        const divGrades = document.querySelector(`div[data-div-teacher-id="${teacherId}"]`);
        divGrades.innerHTML = '';
        if (divGrades) {
            grades.forEach(grade => {
                // si un grado ya esta seleccionado antes de generarlo
                if (selectedSubItemIds.has(String(grade.id_grade))) {
                    const label = document.createElement('label');
                    label.textContent = grade.name;
                    label.dataset.gradeId = grade.id_grade;
                    label.dataset.teacherId = teacherId;
                    label.className = 'label-grade';
                    label.dataset.isSelectedForAsignature = 'false';
                    label.classList.add('hide')
                    label.addEventListener('click', () => {
                        if (label.dataset.isSelectedForAsignature == 'false') {
                            label.dataset.isSelectedForAsignature = 'true';
                            label.classList.add('selected'); // para los estilos al sleccionar

                            selectedSubItemIds.add(String(grade.id_grade));

                            document.querySelectorAll(`label[data-grade-id="${grade.id_grade}"]`)
                                .forEach(l => { if (l !== label) l.classList.add('hide'); });
                        } else {
                            label.dataset.isSelectedForAsignature = 'false';
                            label.classList.remove('selected');
                            selectedSubItemIds.delete(String(grade.id_grade));
                            document.querySelectorAll(`label[data-grade-id="${grade.id_grade}"]`)
                                .forEach(l => { if (l !== label) l.classList.remove('hide'); });
                        }
                    });
                    divGrades.appendChild(label);
                    return;

                };
                // Genera el grado si no se ha seleccionado 
                const label = document.createElement('label');
                label.textContent = grade.name;
                label.dataset.gradeId = grade.id_grade;
                label.className = 'label-grade';
                label.dataset.isSelectedForAsignature = 'false';
                label.dataset.teacherId = teacherId;
                label.addEventListener('click', () => {
                    if (label.dataset.isSelectedForAsignature == 'false') {
                        label.dataset.isSelectedForAsignature = 'true';
                        label.classList.add('selected'); // para los estilos al sleccionar

                        selectedSubItemIds.add(String(grade.id_grade));

                        document.querySelectorAll(`label[data-grade-id="${grade.id_grade}"]`)
                            .forEach(l => { if (l !== label) l.classList.add('hide'); });
                    } else {
                        label.dataset.isSelectedForAsignature = 'false';
                        label.classList.remove('selected');
                        selectedSubItemIds.delete(String(grade.id_grade));
                        document.querySelectorAll(`label[data-grade-id="${grade.id_grade}"]`)
                            .forEach(l => { if (l !== label) l.classList.remove('hide'); });
                    }
                });
                divGrades.appendChild(label);
            });
        };
    } catch (error) {
        console.error('Error loading grades:', error);
        return [];
    }
};
async function loadTeachersListForObjectcs() {
    try {
        const response = await fetch('http://127.0.0.1:5000/api/admin/teachers', {
            method: 'GET',
            headers: { 'Accept': 'application/json' },
            credentials: 'include'
        });
        if (!response.ok) {
            throw new Error('Network response was not ok');
        };
        const data = await response.json();
        const teachers = data.teachers || [];
        const listTeacher = document.getElementById('list-teachers');
        listTeacher.innerHTML = '';
        const grades = await loadGrades();
        teachers.forEach(teacher => {
            const li = document.createElement('li')
            const divGrades = document.createElement('div');
            const labelGrades = document.createElement('label');
            li.textContent = teacher.username;
            li.className = 'li';
            li.dataset.teacherId = teacher.id_teacher;
            divGrades.className = 'div-grade';
            divGrades.dataset.divTeacherId = teacher.id_teacher;
            labelGrades.className = 'label-grades';
            divGrades.dataset.labelTeacherId = teacher.id_teacher;
            listTeacher.appendChild(li)
            listTeacher.appendChild(divGrades);
            divGrades.appendChild(labelGrades);
            li.addEventListener('click', (e) => {
                const div = li.querySelector('.div-grade') || document.querySelector(`div[data-div-teacher-id="${e = teacher.id_teacher}"]`);
                if (div.classList.contains('revelar')) {
                    div.classList.remove('revelar');
                } else {
                    div.classList.add('revelar');
                    if (!div.dataset.loaded) {
                        loadSubItemsList(e = grades, 'data-div-teacher-id', teacher.id_teacher, 'grade', 'teacher', selectedGradesIds, 'isSelectedForAsignature', 'data-grade-id').then(() => { div.dataset.loaded = 'true'; });
                        //loadGradesForTeacher(e = teacher.id_teacher).then(() => { div.dataset.loaded = 'true'; });
                    }
                }
            });
        });
    } catch (error) {
        console.error('Error loading asignatures:', error);
        return;
    }
};
async function createAsignature(nameAsignature) {
    const payload = { name: nameAsignature };
    const res = await fetch('http://127.0.0.1:5000/add_asignature_js', {
        method: 'POST', credentials: 'include', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload)
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.message || 'Error creando nota');
    return data;
};
async function syncTeacherAsignatureAssignment(teacherId, asignatureId, gradeId) {
    const payload = { id_teacher: teacherId, id_asignature: asignatureId, id_grade: gradeId };
    const res = await fetch('http://127.0.0.1:5000/sync_teacher_asignature', {
        method: 'POST', credentials: 'include', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload)
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.message || 'Error creando nota');
    return data;
};
async function openSubjectModal() {
    modalAsignature.classList.add("revelar");
    const teachers = await loadTeachers();
    const grades = await loadGrades();
    loadItemsList(teachers, 'asignature', 'teacher', grades, 'data-teacher-id', 'grade', selectedGradesIds, 'isSelectedForAsignature', 'data-grade-id', loadSubItems = true);
};

async function openItemModal(openModal = false, modalItem, functionLoadItem, nameObject, nameItem, functionLoadSubItems, datasetDivItemId, nameSubItem, selectedGlobalSubItemIds, isSelectedForObject, datasetSubItemId, subItemDataset, loadSubItems, SpItem, SpSubItem) {
    if (openModal) { 
        modalItem.classList.add("revelar");
    }
    const items = await functionLoadItem;
    const subItems = await functionLoadSubItems;
    loadItemsList(items, nameObject, nameItem, subItems, datasetDivItemId, nameSubItem, selectedGlobalSubItemIds, isSelectedForObject, datasetSubItemId, subItemDataset, loadSubItems, SpItem, SpSubItem, false, true, false);
    // teachers, 'teacher', grades, 'data-teacher-id', 'grade', selectedGradesIds, 'isSelectedForAsignature', 'data-grade-id', loadSubItems=true
};

function closeItemModal(nameSubItem, modalItem, nameItem, selectedSubItemIds) {
    const divSubItems = document.querySelectorAll(`.div-${nameSubItem}`);
    modalItem.classList.remove('revelar');
    divSubItems.forEach(divSubItem => {
        divSubItem.classList.remove('revelar');
        divSubItem.innerHTML = ''; // Limpia el contenido del div
    });
    const input = document.getElementById(`input-${nameItem}`);
    input.value = '';
    selectedSubItemIds.clear();
};

function closeSubjectModal() {
    const divSubItems = document.querySelectorAll(".div-grade");
    modalAsignature.classList.remove('revelar');
    divSubItems.forEach(divSubItem => {
        divSubItem.classList.remove('revelar');
    });
    const input = document.getElementById('input-asignature');
    input.value = '';
    selectedGradesIds.clear();
};
async function saveAsignature() {
    modalAsignature.classList.remove('revelar')
    const input = document.getElementById('input-asignature');
    const gradesSelected = document.querySelectorAll(`label[data-is-selected-for-asignature="true"]`);
    const dataAsignature = await createAsignature(input.value);
    const asignatureId = dataAsignature.id;
    if (gradesSelected) {
        gradesSelected.forEach(grade => {
            syncTeacherAsignatureAssignment(grade.dataset.teacherId, asignatureId, grade.dataset.gradeId);
        });
    }
    const divSubItems = document.querySelectorAll(".div-grade");
    divSubItems.forEach(divSubItem => {
        divSubItem.classList.remove('revelar');
    });
    selectedGradesIds.clear();
    // console.log(selectedGradesIds, 'clear');
    input.value = '';
    await loadCardListAsignature();
};

document.addEventListener('DOMContentLoaded', async () => {
    await loadCardListUsers();
    await loadCardListTeacher();
    await loadCardListStudents();
    await loadCardListGrades();
    await loadCardListAsignature();
    //createDivItems();

    // user modal btns
    if (btnOpenAddUSerModal) btnOpenAddUSerModal.addEventListener('click', async () => {
        modalUser.classList.add('revelar');
        const asignatures_grades = await loadAsigGradesForNewTeacher();
        const selectedRole = modalUser.querySelector('select');
        selectedRole.selectedIndex = 0; // Reinicia el select al primer valor (opción por defecto)
        const divs = modalUser.querySelectorAll('.div-user');
        selectedRole.addEventListener('change', async () => {
            if (selectedRole.value === 'teacher') {
                selectedGradesIds.clear();
                let grades = [];
                divs.forEach(div => div.innerHTML='');
                asignatures_grades.forEach(asignature => {
                    asignature.grades.forEach(grade => {
                        grades.push({'name': grade.name, 'id': grade.id}); 
                    });
                    loadItemsList([{'name': asignature.name, 'id': asignature.id}], 'user', 'asignature', grades, 'data-asignature-id-for-user', 'grade', selectedGradesIds, 'isSelectedForUser', 'data-grade-id', '', loadSubItems = true, 'Asignaturas actuales', 'Grados no asignados a la asignatura', oneOption = false, clearList = false, false);   
                    grades = [];
                });
            } else if (selectedRole.value === 'student') { 
                selectedGradesIds.clear();
                divs.forEach(div => div.innerHTML='');
                loadSubItemsList(await loadGrades(), 'data-div-grade-id-for-user', '', 'grade', 'user', selectedGradesIds, 'isSelectedForUser', 'data-grade-id', '', 'Grados para asignar', 'Grado', oneOption = true).then(() => { divs.forEach(div => div.dataset.loaded = 'true'); });
            } else {
                divs.forEach(div => div.innerHTML='');
            }
        });
    });

    if (btnSaveUSer) btnSaveUSer.addEventListener('click', async () => {
        modalUser.classList.remove('revelar');
        const inputUsername = document.getElementById('input-user-name');
        const inputPassword = document.getElementById('input-user-password');
        const selectedRole = modalUser.querySelector('select');
        const institution = document.getElementById('input-user-institution');
        const userId = await saveUser(inputUsername.value, inputPassword.value, selectedRole.value, institution.value);

        if (selectedRole.value === 'teacher') {
            const gradesSelected = document.querySelectorAll(`label[data-is-selected-for-user="true"]`);
            const teacherId = await addTeacher(userId); 
            if (gradesSelected) {
                gradesSelected.forEach(grade => {
                    syncTeacherAsignatureAssignment(teacherId[1], grade.dataset.asignatureId, grade.dataset.gradeId);
                });
            }
        } else if (selectedRole.value === 'student') {
            const gradesSelected = document.querySelectorAll(`label[data-is-selected-for-user="true"]`);
            gradesSelected.forEach(grade => {
                addStudent(userId, grade.dataset.gradeId)
            });
        }

        const inputs = modalUser.querySelectorAll('input');
        inputs.forEach(input => input.value = '');
        selectedRole.selectedIndex = 0; // Reinicia el select al primer valor (opción por defecto)
        selectedGradesIds.clear();

        await loadCardListUsers(addEvent=false);
        await loadCardListTeacher(addEvent=false);
        await loadCardListStudents(addEvent=false)
    })

    if (btnCloseUserModal) btnCloseUserModal.addEventListener('click', () => {
        modalUser.classList.remove('revelar');
        const divSubItems = document.querySelectorAll(".div-user");
        const inputs = modalUser.querySelectorAll('input');
        const selectedRole = modalUser.querySelector('select');
        inputs.forEach(input => input.value = '');
        selectedRole.selectedIndex = 0; // Reinicia el select al primer valor (opción por defecto)
        selectedGradesIds.clear();
        divSubItems.forEach(div => {
            div.classList.remove('revelar');
            div.innerHTML = '';
        });
    });
    // grade modal btns
    if (btnOpenAddGradeModal) btnOpenAddGradeModal.addEventListener('click', () => {
        openItemModal(openModal = true, modalGrade, loadStudentsUndergraduate(), 'grade', 'undergraduatestudent', '', '', '', '', '', '', loadSubItems = false, 'Estudiantes sin grado', 'Grados para asignar');
        openItemModal(openModal = false, modalGrade, loadTeachers(), 'grade', 'teacher', loadAsignatures(), 'data-teacher-id-for-grade', 'asignature', selectedAsignatureIds, 'isSelectedForGrade', 'data-asignature-id', loadSubItems = true, 'Profesores actuales', 'Asignaturas para asignar')
    });
    if (btnCloseGradeModal) btnCloseGradeModal.addEventListener('click', () => {
        closeItemModal('asignature', modalGrade, 'grade', selectedAsignatureIds)
    });

    if (btnSaveGrade) btnSaveGrade.addEventListener('click', saveGrade);

    // Asiganture modal btns
    if (btnOpenAddAsignatureModal) btnOpenAddAsignatureModal.addEventListener('click', () => {
        openItemModal(openModal = true, modalAsignature, loadTeachers(), 'asignature', 'teacher', loadGrades(), 'data-teacher-id-for-asignature', 'grade', selectedGradesIds, 'isSelectedForAsignature', 'data-grade-id', loadSubItems = true, 'Profesores actuales', 'Grados para asignar')
    });
    if (btnCloseAsignatureModal) btnCloseAsignatureModal.addEventListener('click', () => {
        closeItemModal('grade', modalAsignature, 'asignature', selectedGradesIds);
    });
    if (btnSaveAsignature) btnSaveAsignature.addEventListener('click', saveAsignature);
});
