import datetime

class NoteUser:
    def __init__(self, _state, json: dict):
        self.id = json['id']
        self.name = json['name']
        self.username = json['username']
        self.host = json['host']
        self.avatar_url = json['avatarUrl']
        self.avatar_blurhash = json['avatarBlurhash']
        self.avatar_color = json['avatarColor']
        if json.get('instance'):
            self.instance = Instance(_state, json['instance'])
        else:
            self.instance = None
        self.emojis = [Emoji(_state, x) for x in json['emojis']]
        self.online_status = json['onlineStatus']
        self.remote = (_state.host != self.host)

class ClientUser:
    def __init__(self, _state, json: dict):
        self.id = json['id']
        self.name = json['name']
        self.username = json['username']
        self.host = json['host']
        self.avatar_url = json['avatarUrl']
        self.avatar_blurhash = json['avatarBlurhash']
        self.avatar_color = json['avatarColor']
        self.admin = json['isAdmin']
        self.moderator = json['isModerator']
        self.bot = json['isBot']
        self.emojis = [Emoji(_state, x) for x in json['emojis']]
        self.online_status = json['onlineStatus']
        self.url = json['url'] or json['uri']
        self.created_at = datetime.datetime.fromisoformat(json['createdAt'][:-1])
        self.updated_at = datetime.datetime.fromisoformat(json['updatedAt'][:-1])
        self.banner_url = json['bannerUrl']
        self.banner_blurhash = json['bannerBlurhash']
        self.banner_color = json['bannerColor']
        self.locked = json['isLocked']
        self.suspended = json['isSuspended']
        self.silenced = json['isSilenced']
        self.description = json['description']
        self.location = json['location']
        self.birthday = None
        if json['birthday']:
            try:
                self.birthday = datetime.datetime.strptime(json['birthday'], '%Y-%m-%d')
            except ValueError:
                pass
        self.lang = json['lang']
        self.fields = [ProfileField(_state, x) for x in json['fields']]
        self.followers_count = json['followersCount']
        self.following_count = json['followingCount']
        self.notes_count = json['notesCount']
        self.pinned_note_ids = json['pinnedNoteIds']
        self.pinned_notes = [Note(_state, x) for x in json['pinnedNotes']]

class ProfileField:
    def __init__(self, _state, json: dict):
        self.name = json['name']
        self.value = json['value']


class Instance:
    def __init__(self, _state, json: dict):
        self.name = json['name']
        self.software_name = json['softwareName']
        self.software_version = json['softwareVersion']
        self.icon_url = json['iconUrl']
        self.favicon_url = json['faviconUrl']
        self.theme_color = json['themeColor']

class Emoji:
    def __init__(self, _state, json: dict):
        self.name = json['name']
        self.url = json['url']

class File:
    def __init__(self, _state, json: dict):
        self.id = json['id']
        self.created_at = datetime.datetime.fromisoformat(json['createdAt'][:-1])
        self.name = json['name']
        self.url = json.get('url') or json.get('uri')
        self.thumbnail_url = json['thumbnailUrl']
        self.size = json['size']
        self.type = json['type']
        self.comment = json['comment']
        self.is_sensitive = json['isSensitive']
        self.blurhash = json['blurhash']
        self.properties = FileProperties(_state, json['properties'])
        self.folder_id = json['folderId']
        self.folder = json['folder']
        self.user_id = json['userId']
        self.user = None
        if json['user']:
            self.user = NoteUser(_state, json['user'])

class FileProperties:
    def __init__(self, _state, json: dict):
        self.width = json.get('width')
        self.height = json.get('height')

class Note:

    def fromAPIResult(self, _state, json: dict):
        return Note(_state, json['createdNote'])

    def __init__(self, _state, json: dict):
        self.id = json.get('id', '')
        self.created_at = None
        self.created_at = datetime.datetime.fromisoformat(json['createdAt'][:-1])
        self.author = NoteUser(_state, json['user'])
        self.text = json.get('text')
        self.cw = json.get('cw')
        self.visibility = json['visibility']
        self.renote_count = json['renoteCount']
        self.replies_count = json['repliesCount']
        self.reactions = json['reactions']
        self.emojis = [Emoji(_state, x) for x in json['emojis']]
        self.files = [File(_state, x) for x in json['files']]
        self.file_ids = json['fileIds']
        self.reply_id = json['replyId']
        self.renote_id = json['renoteId']
        self.mentions = json.get('mentions') or []
        self.url = json.get('url') or json.get('uri')
        self._state = _state
    
    async def delete(self):
        if self._state.user.id != self.author.id:
            raise PermissionError('You are not the author of this note.')
        self._state.api.notes_delete(self.id)
    
    async def pin(self):
        if self._state.user.id != self.author.id:
            raise PermissionError('You are not the author of this note.')
        self._state.api.i_pin(self.id)
    
    async def unpin(self):
        if self._state.user.id != self.author.id:
            raise PermissionError('You are not the author of this note.')
        self._state.api.i_unpin(self.id)

    async def reply(self, *args, **kwargs):
        d = self._state.api.notes_create(reply_id=self.id, *args, **kwargs)
        return Note(self._state, d)
    
    async def renote(self):
        d = self._state.api.notes_create(renote_id=self.id)
