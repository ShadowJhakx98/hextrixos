const express = require('express');
const fs = require('fs');
const path = require('path');
const { spawn, exec } = require('child_process');
const { promisify } = require('util');
const os = require('os');

const app = express();
const PORT = process.env.PORT || 3000;
const execPromise = promisify(exec);

// Middleware for parsing JSON
app.use(express.json());

// MCP API routes
app.post('/v1/filesystem/read', async (req, res) => {
  try {
    const { path: filePath } = req.body;
    if (!filePath) {
      return res.status(400).json({ error: 'Path is required' });
    }

    if (!fs.existsSync(filePath)) {
      return res.status(404).json({ error: 'File not found' });
    }

    const content = fs.readFileSync(filePath, 'utf8');
    res.json({ content });
  } catch (error) {
    console.error('Error reading file:', error);
    res.status(500).json({ error: 'Failed to read file' });
  }
});

app.post('/v1/filesystem/write', async (req, res) => {
  try {
    const { path: filePath, content } = req.body;
    if (!filePath || content === undefined) {
      return res.status(400).json({ error: 'Path and content are required' });
    }

    // Ensure the directory exists
    const dirPath = path.dirname(filePath);
    if (!fs.existsSync(dirPath)) {
      fs.mkdirSync(dirPath, { recursive: true });
    }

    fs.writeFileSync(filePath, content);
    res.json({ success: true });
  } catch (error) {
    console.error('Error writing file:', error);
    res.status(500).json({ error: 'Failed to write file' });
  }
});

app.post('/v1/filesystem/list', async (req, res) => {
  try {
    const { path: dirPath } = req.body;
    if (!dirPath) {
      return res.status(400).json({ error: 'Path is required' });
    }

    if (!fs.existsSync(dirPath) || !fs.statSync(dirPath).isDirectory()) {
      return res.status(404).json({ error: 'Directory not found' });
    }

    const entries = fs.readdirSync(dirPath, { withFileTypes: true });
    const files = entries.map(entry => ({
      name: entry.name,
      type: entry.isDirectory() ? 'directory' : 'file',
      path: path.join(dirPath, entry.name)
    }));

    res.json({ files });
  } catch (error) {
    console.error('Error listing directory:', error);
    res.status(500).json({ error: 'Failed to list directory' });
  }
});

// New endpoint: File search
app.post('/v1/filesystem/search', async (req, res) => {
  try {
    const { path: dirPath, pattern, recursive = true, maxResults = 100 } = req.body;
    if (!dirPath || !pattern) {
      return res.status(400).json({ error: 'Path and pattern are required' });
    }

    if (!fs.existsSync(dirPath)) {
      return res.status(404).json({ error: 'Directory not found' });
    }

    const cmd = `find ${dirPath} ${recursive ? '' : '-maxdepth 1'} -type f -name "${pattern}" -print | head -n ${maxResults}`;
    const { stdout, stderr } = await execPromise(cmd);

    if (stderr) {
      console.error('Search error:', stderr);
    }

    const results = stdout.trim().split('\n').filter(Boolean);
    res.json({ results });
  } catch (error) {
    console.error('Error searching files:', error);
    res.status(500).json({ error: 'Failed to search files' });
  }
});

// New endpoint: Grep for text in files
app.post('/v1/filesystem/grep', async (req, res) => {
  try {
    const { path: dirPath, query, recursive = true, maxResults = 100 } = req.body;
    if (!dirPath || !query) {
      return res.status(400).json({ error: 'Path and query are required' });
    }

    if (!fs.existsSync(dirPath)) {
      return res.status(404).json({ error: 'Directory not found' });
    }

    const cmd = `grep -${recursive ? 'r' : ''} -l "${query}" ${dirPath} | head -n ${maxResults}`;
    const { stdout, stderr } = await execPromise(cmd);

    if (stderr) {
      console.error('Grep error:', stderr);
    }

    // Format results
    const results = stdout.trim().split('\n').filter(Boolean).map(file => ({
      file,
      matches: []
    }));

    // For each file, get the matching lines
    for (const item of results) {
      try {
        const lineCmd = `grep -n "${query}" "${item.file}" | head -n 10`;
        const { stdout: lineStdout } = await execPromise(lineCmd);
        
        item.matches = lineStdout.trim().split('\n').filter(Boolean).map(line => {
          const [lineNum, ...rest] = line.split(':');
          return {
            line: parseInt(lineNum),
            content: rest.join(':')
          };
        });
      } catch (error) {
        console.error(`Error getting lines for ${item.file}:`, error);
      }
    }

    res.json({ results });
  } catch (error) {
    console.error('Error grepping files:', error);
    res.status(500).json({ error: 'Failed to grep files' });
  }
});

// Hextrix OS specific commands
app.post('/v1/hextrix/execute', async (req, res) => {
  try {
    const { command, args = [] } = req.body;
    if (!command) {
      return res.status(400).json({ error: 'Command is required' });
    }

    const process = spawn(command, args);
    let stdout = '';
    let stderr = '';

    process.stdout.on('data', (data) => {
      stdout += data.toString();
    });

    process.stderr.on('data', (data) => {
      stderr += data.toString();
    });

    process.on('close', (code) => {
      res.json({
        exitCode: code,
        stdout,
        stderr
      });
    });
  } catch (error) {
    console.error('Error executing command:', error);
    res.status(500).json({ error: 'Failed to execute command' });
  }
});

// Hextrix App Endpoints

// Notepad app
app.post('/v1/hextrix/apps/notepad/open', async (req, res) => {
  try {
    const { filePath } = req.body;
    const args = filePath ? [filePath] : [];
    
    const result = spawn('python3', ['/home/jared/hextrix-ai-os-env/hud/hextrix-notepad.py', ...args], { 
      detached: true,
      stdio: 'ignore' 
    });
    
    // Unref the child process so it can run independently
    result.unref();
    
    res.json({ success: true, message: 'Notepad launched' });
  } catch (error) {
    console.error('Error launching notepad:', error);
    res.status(500).json({ error: 'Failed to launch notepad' });
  }
});

// New endpoint: Create note and save
app.post('/v1/hextrix/apps/notepad/create', async (req, res) => {
  try {
    const { title, content, tags = [], folder = 'Notes' } = req.body;
    
    if (!title || !content) {
      return res.status(400).json({ error: 'Title and content are required' });
    }
    
    // Create notes directory if it doesn't exist
    const notesDir = path.join('/home/jared/hextrix-ai-os-env/data/notes', folder);
    if (!fs.existsSync(notesDir)) {
      fs.mkdirSync(notesDir, { recursive: true });
    }
    
    // Create a safe filename from the title
    const safeTitle = title.replace(/[^a-z0-9]/gi, '_').toLowerCase();
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const fileName = `${safeTitle}-${timestamp}.txt`;
    const filePath = path.join(notesDir, fileName);
    
    // Create note metadata
    const metadata = {
      title,
      created: new Date().toISOString(),
      tags,
      folder
    };
    
    // Combine metadata and content
    const fullContent = `--- METADATA ---\n${JSON.stringify(metadata, null, 2)}\n\n--- CONTENT ---\n${content}`;
    
    // Write the file
    fs.writeFileSync(filePath, fullContent);
    
    res.json({ 
      success: true, 
      message: 'Note created successfully',
      note: {
        title,
        path: filePath,
        created: metadata.created,
        tags,
        folder
      }
    });
  } catch (error) {
    console.error('Error creating note:', error);
    res.status(500).json({ error: 'Failed to create note' });
  }
});

// New endpoint: List all notes
app.get('/v1/hextrix/apps/notepad/list', async (req, res) => {
  try {
    const { folder = 'Notes', tag = null } = req.query;
    const notesDir = path.join('/home/jared/hextrix-ai-os-env/data/notes', folder);
    
    if (!fs.existsSync(notesDir)) {
      return res.json({ notes: [] }); // Return empty array if directory doesn't exist
    }
    
    // Get all note files
    const files = fs.readdirSync(notesDir).filter(file => file.endsWith('.txt'));
    const notes = [];
    
    // Process each file
    for (const file of files) {
      try {
        const filePath = path.join(notesDir, file);
        const content = fs.readFileSync(filePath, 'utf8');
        
        // Extract metadata
        const metadataMatch = content.match(/--- METADATA ---\n([\s\S]*?)\n\n--- CONTENT ---/);
        if (metadataMatch) {
          const metadata = JSON.parse(metadataMatch[1]);
          
          // Filter by tag if specified
          if (tag && (!metadata.tags || !metadata.tags.includes(tag))) {
            continue;
          }
          
          notes.push({
            title: metadata.title,
            path: filePath,
            created: metadata.created,
            tags: metadata.tags || [],
            folder: metadata.folder || folder
          });
        }
      } catch (error) {
        console.error(`Error processing note file ${file}:`, error);
      }
    }
    
    res.json({ notes });
  } catch (error) {
    console.error('Error listing notes:', error);
    res.status(500).json({ error: 'Failed to list notes' });
  }
});

// Email app
app.post('/v1/hextrix/apps/email/open', async (req, res) => {
  try {
    spawn('python3', ['/home/jared/hextrix-ai-os-env/hud/hextrix-email.py'], { 
      detached: true,
      stdio: 'ignore' 
    }).unref();
    
    res.json({ success: true, message: 'Email app launched' });
  } catch (error) {
    console.error('Error launching email app:', error);
    res.status(500).json({ error: 'Failed to launch email app' });
  }
});

// New endpoint: Compose email (save as draft)
app.post('/v1/hextrix/apps/email/compose', async (req, res) => {
  try {
    const { to, subject, body, attachments = [] } = req.body;
    
    if (!to || !subject || !body) {
      return res.status(400).json({ error: 'To, subject, and body are required' });
    }
    
    // Create drafts directory if it doesn't exist
    const draftsDir = '/home/jared/hextrix-ai-os-env/data/email/drafts';
    if (!fs.existsSync(draftsDir)) {
      fs.mkdirSync(draftsDir, { recursive: true });
    }
    
    // Create a draft email
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const draftId = `draft-${timestamp}`;
    const draftPath = path.join(draftsDir, `${draftId}.json`);
    
    const draft = {
      id: draftId,
      to,
      subject,
      body,
      attachments,
      created: new Date().toISOString(),
      status: 'draft'
    };
    
    // Write the draft to a file
    fs.writeFileSync(draftPath, JSON.stringify(draft, null, 2));
    
    // Optionally launch the email app with this draft
    spawn('python3', ['/home/jared/hextrix-ai-os-env/hud/hextrix-email.py', '--draft', draftId], { 
      detached: true,
      stdio: 'ignore' 
    }).unref();
    
    res.json({ 
      success: true, 
      message: 'Email draft created',
      draft: {
        id: draftId,
        to,
        subject,
        created: draft.created
      }
    });
  } catch (error) {
    console.error('Error creating email draft:', error);
    res.status(500).json({ error: 'Failed to create email draft' });
  }
});

// Calculator app
app.post('/v1/hextrix/apps/calculator/open', async (req, res) => {
  try {
    spawn('python3', ['/home/jared/hextrix-ai-os-env/hud/hextrix-calculator.py'], { 
      detached: true,
      stdio: 'ignore' 
    }).unref();
    
    res.json({ success: true, message: 'Calculator launched' });
  } catch (error) {
    console.error('Error launching calculator:', error);
    res.status(500).json({ error: 'Failed to launch calculator' });
  }
});

// New endpoint: Perform calculation
app.post('/v1/hextrix/apps/calculator/calculate', async (req, res) => {
  try {
    const { expression } = req.body;
    
    if (!expression) {
      return res.status(400).json({ error: 'Expression is required' });
    }
    
    // Sanitize the expression for safety
    const sanitizedExpression = expression.replace(/[^0-9+\-*/().\s]/g, '');
    
    // Use Node.js eval() for simple calculations - be careful with this in production!
    // A better approach would be to use a math expression parser library
    let result;
    try {
      // eslint-disable-next-line no-eval
      result = eval(sanitizedExpression);
    } catch (calcError) {
      return res.status(400).json({ error: 'Invalid expression' });
    }
    
    res.json({ 
      success: true,
      expression: sanitizedExpression,
      result
    });
  } catch (error) {
    console.error('Error calculating:', error);
    res.status(500).json({ error: 'Failed to calculate' });
  }
});

// Health app
app.post('/v1/hextrix/apps/health/open', async (req, res) => {
  try {
    spawn('python3', ['/home/jared/hextrix-ai-os-env/hud/hextrix-health.py'], { 
      detached: true,
      stdio: 'ignore' 
    }).unref();
    
    res.json({ success: true, message: 'Health app launched' });
  } catch (error) {
    console.error('Error launching health app:', error);
    res.status(500).json({ error: 'Failed to launch health app' });
  }
});

// New endpoint: Log health data
app.post('/v1/hextrix/apps/health/log', async (req, res) => {
  try {
    const { type, value, unit, timestamp = new Date().toISOString(), notes = '' } = req.body;
    
    if (!type || value === undefined) {
      return res.status(400).json({ error: 'Type and value are required' });
    }
    
    // Create health data directory if it doesn't exist
    const healthDir = '/home/jared/hextrix-ai-os-env/data/health';
    if (!fs.existsSync(healthDir)) {
      fs.mkdirSync(healthDir, { recursive: true });
    }
    
    // Load existing data file or create a new one
    const dataFile = path.join(healthDir, 'health_logs.json');
    let healthData = [];
    
    if (fs.existsSync(dataFile)) {
      try {
        const fileContent = fs.readFileSync(dataFile, 'utf8');
        healthData = JSON.parse(fileContent);
      } catch (parseError) {
        console.error('Error parsing health data file:', parseError);
      }
    }
    
    // Add new entry
    const entry = {
      id: `log-${Date.now()}`,
      type,
      value,
      unit,
      timestamp,
      notes
    };
    
    healthData.push(entry);
    
    // Save data back to file
    fs.writeFileSync(dataFile, JSON.stringify(healthData, null, 2));
    
    res.json({ 
      success: true, 
      message: 'Health data logged',
      entry
    });
  } catch (error) {
    console.error('Error logging health data:', error);
    res.status(500).json({ error: 'Failed to log health data' });
  }
});

// Calendar app
app.post('/v1/hextrix/apps/calendar/open', async (req, res) => {
  try {
    spawn('python3', ['/home/jared/hextrix-ai-os-env/hud/hextrix-calendar.py'], { 
      detached: true,
      stdio: 'ignore' 
    }).unref();
    
    res.json({ success: true, message: 'Calendar app launched' });
  } catch (error) {
    console.error('Error launching calendar app:', error);
    res.status(500).json({ error: 'Failed to launch calendar app' });
  }
});

// New endpoint: Add calendar event
app.post('/v1/hextrix/apps/calendar/add-event', async (req, res) => {
  try {
    const { 
      title, 
      start, 
      end, 
      allDay = false, 
      location = '', 
      description = '', 
      participants = [],
      reminder = 15 // minutes before
    } = req.body;
    
    if (!title || !start) {
      return res.status(400).json({ error: 'Title and start time are required' });
    }
    
    // Create calendar data directory if it doesn't exist
    const calendarDir = '/home/jared/hextrix-ai-os-env/data/calendar';
    if (!fs.existsSync(calendarDir)) {
      fs.mkdirSync(calendarDir, { recursive: true });
    }
    
    // Load existing events or create a new file
    const eventsFile = path.join(calendarDir, 'events.json');
    let events = [];
    
    if (fs.existsSync(eventsFile)) {
      try {
        const fileContent = fs.readFileSync(eventsFile, 'utf8');
        events = JSON.parse(fileContent);
      } catch (parseError) {
        console.error('Error parsing events file:', parseError);
      }
    }
    
    // Create a new event
    const event = {
      id: `event-${Date.now()}`,
      title,
      start,
      end: end || start, // If no end provided, use start time
      allDay,
      location,
      description,
      participants,
      reminder,
      created: new Date().toISOString()
    };
    
    events.push(event);
    
    // Save events back to file
    fs.writeFileSync(eventsFile, JSON.stringify(events, null, 2));
    
    // Optionally open the calendar app to show the new event
    spawn('python3', ['/home/jared/hextrix-ai-os-env/hud/hextrix-calendar.py', '--event', event.id], { 
      detached: true,
      stdio: 'ignore' 
    }).unref();
    
    res.json({ 
      success: true, 
      message: 'Event added successfully',
      event
    });
  } catch (error) {
    console.error('Error adding calendar event:', error);
    res.status(500).json({ error: 'Failed to add calendar event' });
  }
});

// New endpoint: List calendar events
app.get('/v1/hextrix/apps/calendar/events', async (req, res) => {
  try {
    const { start, end } = req.query;
    
    const calendarDir = '/home/jared/hextrix-ai-os-env/data/calendar';
    const eventsFile = path.join(calendarDir, 'events.json');
    
    if (!fs.existsSync(eventsFile)) {
      return res.json({ events: [] }); // Return empty array if file doesn't exist
    }
    
    // Load events
    const fileContent = fs.readFileSync(eventsFile, 'utf8');
    let events = JSON.parse(fileContent);
    
    // Filter events by date range if specified
    if (start && end) {
      const startDate = new Date(start);
      const endDate = new Date(end);
      
      events = events.filter(event => {
        const eventStart = new Date(event.start);
        return eventStart >= startDate && eventStart <= endDate;
      });
    }
    
    res.json({ events });
  } catch (error) {
    console.error('Error listing calendar events:', error);
    res.status(500).json({ error: 'Failed to list calendar events' });
  }
});

// Contacts app
app.post('/v1/hextrix/apps/contacts/open', async (req, res) => {
  try {
    spawn('python3', ['/home/jared/hextrix-ai-os-env/hud/hextrix-contacts.py'], { 
      detached: true,
      stdio: 'ignore' 
    }).unref();
    
    res.json({ success: true, message: 'Contacts app launched' });
  } catch (error) {
    console.error('Error launching contacts app:', error);
    res.status(500).json({ error: 'Failed to launch contacts app' });
  }
});

// New endpoint: Add contact
app.post('/v1/hextrix/apps/contacts/add', async (req, res) => {
  try {
    const { 
      name, 
      email = '', 
      phone = '', 
      address = '', 
      company = '', 
      notes = '', 
      groups = [] 
    } = req.body;
    
    if (!name) {
      return res.status(400).json({ error: 'Contact name is required' });
    }
    
    // Create contacts directory if it doesn't exist
    const contactsDir = '/home/jared/hextrix-ai-os-env/data/contacts';
    if (!fs.existsSync(contactsDir)) {
      fs.mkdirSync(contactsDir, { recursive: true });
    }
    
    // Load existing contacts or create a new file
    const contactsFile = path.join(contactsDir, 'contacts.json');
    let contacts = [];
    
    if (fs.existsSync(contactsFile)) {
      try {
        const fileContent = fs.readFileSync(contactsFile, 'utf8');
        contacts = JSON.parse(fileContent);
      } catch (parseError) {
        console.error('Error parsing contacts file:', parseError);
      }
    }
    
    // Create a new contact
    const contact = {
      id: `contact-${Date.now()}`,
      name,
      email,
      phone,
      address,
      company,
      notes,
      groups,
      created: new Date().toISOString()
    };
    
    contacts.push(contact);
    
    // Save contacts back to file
    fs.writeFileSync(contactsFile, JSON.stringify(contacts, null, 2));
    
    res.json({ 
      success: true, 
      message: 'Contact added successfully',
      contact
    });
  } catch (error) {
    console.error('Error adding contact:', error);
    res.status(500).json({ error: 'Failed to add contact' });
  }
});

// New endpoint: Search contacts
app.get('/v1/hextrix/apps/contacts/search', async (req, res) => {
  try {
    const { query, group } = req.query;
    
    const contactsDir = '/home/jared/hextrix-ai-os-env/data/contacts';
    const contactsFile = path.join(contactsDir, 'contacts.json');
    
    if (!fs.existsSync(contactsFile)) {
      return res.json({ contacts: [] }); // Return empty array if file doesn't exist
    }
    
    // Load contacts
    const fileContent = fs.readFileSync(contactsFile, 'utf8');
    let contacts = JSON.parse(fileContent);
    
    // Filter contacts
    if (query) {
      const searchQuery = query.toLowerCase();
      contacts = contacts.filter(contact => 
        contact.name.toLowerCase().includes(searchQuery) || 
        contact.email.toLowerCase().includes(searchQuery) || 
        contact.company.toLowerCase().includes(searchQuery)
      );
    }
    
    if (group) {
      contacts = contacts.filter(contact => 
        contact.groups && contact.groups.includes(group)
      );
    }
    
    res.json({ contacts });
  } catch (error) {
    console.error('Error searching contacts:', error);
    res.status(500).json({ error: 'Failed to search contacts' });
  }
});

// App Center
app.post('/v1/hextrix/apps/appcenter/open', async (req, res) => {
  try {
    spawn('python3', ['/home/jared/hextrix-ai-os-env/hud/hextrix-app-center.py'], { 
      detached: true,
      stdio: 'ignore' 
    }).unref();
    
    res.json({ success: true, message: 'App Center launched' });
  } catch (error) {
    console.error('Error launching app center:', error);
    res.status(500).json({ error: 'Failed to launch app center' });
  }
});

// List available apps
app.get('/v1/hextrix/apps/list', async (req, res) => {
  try {
    const apps = [
      { id: 'notepad', name: 'Notepad', path: '/home/jared/hextrix-ai-os-env/hud/hextrix-notepad.py' },
      { id: 'email', name: 'Email', path: '/home/jared/hextrix-ai-os-env/hud/hextrix-email.py' },
      { id: 'calculator', name: 'Calculator', path: '/home/jared/hextrix-ai-os-env/hud/hextrix-calculator.py' },
      { id: 'health', name: 'Health', path: '/home/jared/hextrix-ai-os-env/hud/hextrix-health.py' },
      { id: 'calendar', name: 'Calendar', path: '/home/jared/hextrix-ai-os-env/hud/hextrix-calendar.py' },
      { id: 'contacts', name: 'Contacts', path: '/home/jared/hextrix-ai-os-env/hud/hextrix-contacts.py' },
      { id: 'appcenter', name: 'App Center', path: '/home/jared/hextrix-ai-os-env/hud/hextrix-app-center.py' }
    ];
    
    res.json({ apps });
  } catch (error) {
    console.error('Error listing apps:', error);
    res.status(500).json({ error: 'Failed to list apps' });
  }
});

// HexWin endpoints
app.post('/v1/hextrix/apps/hexwin/open', async (req, res) => {
  try {
    spawn('python3', ['/home/jared/hextrix-ai-os-env/hud/hextrix-hexwin.py'], { 
      detached: true,
      stdio: 'ignore' 
    }).unref();
    
    res.json({ success: true, message: 'HexWin launched' });
  } catch (error) {
    console.error('Error launching HexWin:', error);
    res.status(500).json({ error: 'Failed to launch HexWin' });
  }
});

// Run Windows application
app.post('/v1/hextrix/apps/hexwin/run', async (req, res) => {
  try {
    const { path: exePath } = req.body;
    
    if (!exePath) {
      return res.status(400).json({ error: 'Executable path is required' });
    }
    
    if (!fs.existsSync(exePath)) {
      return res.status(404).json({ error: 'Executable not found' });
    }
    
    const homeDir = os.homedir();
    const result = spawn(path.join(homeDir, '.hexwin', 'hexwin-run.sh'), [exePath], { 
      detached: true,
      stdio: 'ignore' 
    });
    
    result.unref();
    
    res.json({ success: true, message: 'Windows application launched' });
  } catch (error) {
    console.error('Error running Windows application:', error);
    res.status(500).json({ error: 'Failed to run Windows application' });
  }
});

// Install Windows application
app.post('/v1/hextrix/apps/hexwin/install', async (req, res) => {
  try {
    const { installer, name, category = 'Windows' } = req.body;
    
    if (!installer || !name) {
      return res.status(400).json({ error: 'Installer path and name are required' });
    }
    
    if (!fs.existsSync(installer)) {
      return res.status(404).json({ error: 'Installer not found' });
    }
    
    const homeDir = os.homedir();
    const process = spawn(path.join(homeDir, '.hexwin', 'hexwin-install.sh'), [
      '-n', name,
      '-c', category,
      installer
    ]);
    
    let stdout = '';
    let stderr = '';
    
    process.stdout.on('data', (data) => {
      stdout += data.toString();
    });
    
    process.stderr.on('data', (data) => {
      stderr += data.toString();
    });
    
    process.on('close', (code) => {
      if (code === 0) {
        res.json({
          success: true,
          message: `Successfully installed ${name}`,
          output: stdout
        });
      } else {
        res.status(500).json({
          success: false,
          message: `Failed to install ${name}`,
          error: stderr,
          output: stdout
        });
      }
    });
  } catch (error) {
    console.error('Error installing Windows application:', error);
    res.status(500).json({ error: 'Failed to install Windows application' });
  }
});

// List installed Windows applications
app.get('/v1/hextrix/apps/hexwin/list', async (req, res) => {
  try {
    const homeDir = os.homedir();
    const appsFile = path.join(homeDir, '.hexwin', 'appdata', 'installed_apps.json');
    
    if (!fs.existsSync(appsFile)) {
      return res.json({ apps: [] });
    }
    
    const content = fs.readFileSync(appsFile, 'utf8');
    const apps = JSON.parse(content);
    
    res.json({ apps });
  } catch (error) {
    console.error('Error listing Windows applications:', error);
    res.status(500).json({ error: 'Failed to list Windows applications' });
  }
});

// MCP discovery endpoint
app.get('/.well-known/mcp-configuration', (req, res) => {
  res.json({
    name: 'Hextrix OS MCP',
    version: '1.0.0',
    description: 'MCP connector for Hextrix OS',
    capabilities: [
      'filesystem.read',
      'filesystem.write',
      'filesystem.list',
      'filesystem.search',
      'filesystem.grep',
      'hextrix.execute',
      'hextrix.apps.notepad',
      'hextrix.apps.notepad.create',
      'hextrix.apps.notepad.list',
      'hextrix.apps.email',
      'hextrix.apps.email.compose',
      'hextrix.apps.calculator',
      'hextrix.apps.calculator.calculate',
      'hextrix.apps.health',
      'hextrix.apps.health.log',
      'hextrix.apps.calendar',
      'hextrix.apps.calendar.addevent',
      'hextrix.apps.calendar.events',
      'hextrix.apps.contacts',
      'hextrix.apps.contacts.add',
      'hextrix.apps.contacts.search',
      'hextrix.apps.appcenter',
      'hextrix.apps.list',
      'hextrix.apps.hexwin',
      'hextrix.apps.hexwin.run',
      'hextrix.apps.hexwin.install',
      'hextrix.apps.hexwin.list'
    ]
  });
});

// HexDroid API routes
app.get('/api/hexdroid/capabilities', (req, res) => {
  res.json({
    success: true,
    capabilities: [
      'app_installation',
      'app_uninstallation', 
      'app_launch',
      'app_list',
      'runtime_management',
      'adb_shell'
    ]
  });
});

app.get('/api/hexdroid/list', (req, res) => {
  try {
    const dataDir = path.join(os.homedir(), '.hexdroid', 'appdata');
    const appsFile = path.join(dataDir, 'installed_apps.json');
    
    if (fs.existsSync(appsFile)) {
      const appData = JSON.parse(fs.readFileSync(appsFile, 'utf8'));
      res.json({ success: true, apps: appData });
    } else {
      res.json({ success: true, apps: [] });
    }
  } catch (error) {
    res.json({ success: false, error: error.message });
  }
});

app.post('/api/hexdroid/install', (req, res) => {
  try {
    const { apk_path, runtime, app_name, icon_path } = req.body;
    
    if (!apk_path) {
      return res.json({ success: false, error: 'APK path is required' });
    }
    
    let command = `${path.join(os.homedir(), '.hexdroid', 'hexdroid-install.sh')}`;
    
    if (runtime) {
      command += ` --runtime ${runtime}`;
    }
    
    if (app_name) {
      command += ` --name "${app_name}"`;
    }
    
    if (icon_path) {
      command += ` --icon "${icon_path}"`;
    }
    
    command += ` "${apk_path}"`;
    
    exec(command, (error, stdout, stderr) => {
      if (error) {
        return res.json({ success: false, error: stderr || error.message });
      }
      res.json({ success: true, message: 'Application installed successfully', output: stdout });
    });
  } catch (error) {
    res.json({ success: false, error: error.message });
  }
});

app.post('/api/hexdroid/uninstall', (req, res) => {
  try {
    const { app_id } = req.body;
    
    if (!app_id) {
      return res.json({ success: false, error: 'App ID is required' });
    }
    
    const command = `${path.join(os.homedir(), '.hexdroid', 'hexdroid-uninstall.sh')} ${app_id}`;
    
    exec(command, (error, stdout, stderr) => {
      if (error) {
        return res.json({ success: false, error: stderr || error.message });
      }
      res.json({ success: true, message: 'Application uninstalled successfully', output: stdout });
    });
  } catch (error) {
    res.json({ success: false, error: error.message });
  }
});

app.post('/api/hexdroid/launch', (req, res) => {
  try {
    const { app_id, runtime } = req.body;
    
    if (!app_id) {
      return res.json({ success: false, error: 'App ID is required' });
    }
    
    // Find the app's package name from installed apps
    const dataDir = path.join(os.homedir(), '.hexdroid', 'appdata');
    const appsFile = path.join(dataDir, 'installed_apps.json');
    
    if (!fs.existsSync(appsFile)) {
      return res.json({ success: false, error: 'No apps database found' });
    }
    
    const apps = JSON.parse(fs.readFileSync(appsFile, 'utf8'));
    const app = apps.find(a => a.id === app_id);
    
    if (!app) {
      return res.json({ success: false, error: 'App not found' });
    }
    
    let command;
    const packageName = app.package;
    const appRuntime = runtime || app.runtime;
    
    if (appRuntime === 'anbox') {
      command = `anbox launch --package=${packageName} --component=${packageName}.MainActivity`;
    } else if (appRuntime === 'waydroid') {
      command = `waydroid app launch ${packageName}`;
    } else {
      return res.json({ success: false, error: 'Invalid runtime specified' });
    }
    
    exec(command, (error, stdout, stderr) => {
      if (error) {
        return res.json({ success: false, error: stderr || error.message });
      }
      res.json({ success: true, message: 'Application launched successfully' });
    });
  } catch (error) {
    res.json({ success: false, error: error.message });
  }
});

app.post('/api/hexdroid/runtime/restart', (req, res) => {
  try {
    const { runtime } = req.body;
    
    if (!runtime || (runtime !== 'anbox' && runtime !== 'waydroid')) {
      return res.json({ success: false, error: 'Valid runtime (anbox or waydroid) is required' });
    }
    
    let command;
    
    if (runtime === 'anbox') {
      command = 'systemctl --user restart anbox.service';
    } else {
      command = 'waydroid session stop && sleep 2 && waydroid session start';
    }
    
    exec(command, (error, stdout, stderr) => {
      if (error) {
        return res.json({ success: false, error: stderr || error.message });
      }
      res.json({ success: true, message: `${runtime.charAt(0).toUpperCase() + runtime.slice(1)} runtime restarted successfully` });
    });
  } catch (error) {
    res.json({ success: false, error: error.message });
  }
});

app.get('/api/hexdroid/runtime/status', (req, res) => {
  try {
    // Check Anbox status
    exec('systemctl --user is-active anbox.service', (anboxError, anboxStdout) => {
      const anboxStatus = anboxError ? 'Stopped' : 'Running';
      
      // Check Waydroid status
      exec('waydroid status', (waydroidError, waydroidStdout) => {
        const waydroidStatus = waydroidStdout && waydroidStdout.includes('RUNNING') ? 'Running' : 'Stopped';
        
        res.json({
          success: true,
          status: {
            anbox: anboxStatus,
            waydroid: waydroidStatus
          }
        });
      });
    });
  } catch (error) {
    res.json({ success: false, error: error.message });
  }
});

// Add HexDroid capabilities to the main capabilities list
app.get('/api/capabilities', (req, res) => {
  const capabilities = [
    // ... existing capabilities ...
    
    // HexDroid capabilities
    'hexdroid_app_installation',
    'hexdroid_app_uninstallation',
    'hexdroid_app_launch',
    'hexdroid_app_list',
    'hexdroid_runtime_management'
  ];
  
  res.json({
    success: true,
    capabilities: capabilities
  });
});

// Start the server
app.listen(PORT, () => {
  console.log(`Hextrix OS MCP server running on port ${PORT}`);
}); 