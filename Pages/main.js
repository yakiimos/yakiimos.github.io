// 假设 JSON 文件的路径为 'data.json'
fetch('sites.json')
  .then(response => {
    if (!response.ok) {
      throw new Error('Network response was not ok ' + response.statusText);
    }
    return response.json();
  })
  .then(data => {
    // 调用函数将 JSON 数据渲染为表格
    renderTable(data);
  })
  .catch(error => {
    console.error('There was a problem with the fetch operation:', error);
  });

// 将 JSON 数据渲染为表格
function renderTable(data) {
  const table = document.createElement('table');
  table.border = '1';

  // 创建表头
  const thead = document.createElement('thead');
  const headerRow = document.createElement('tr');
  Object.keys(data[0]).forEach(key => {
    const th = document.createElement('th');
    th.textContent = key;
    headerRow.appendChild(th);
  });
  thead.appendChild(headerRow);
  table.appendChild(thead);

  // 创建表格内容
  const tbody = document.createElement('tbody');
  data.forEach(item => {
    const row = document.createElement('tr');
    Object.values(item).forEach(value => {
      const td = document.createElement('td');
      td.textContent = value;
      row.appendChild(td);
    });
    tbody.appendChild(row);
  });
  table.appendChild(tbody);

  // 将表格添加到页面
  document.body.appendChild(table);
}