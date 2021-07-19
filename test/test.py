import filetype
import json

def main():
    kind = filetype.guess('20743693.jpg')
    if kind is None:
        print('Cannot guess file type!')
        return

    print('File extension: %s' % kind.is_extension)
    print('File MIME type: %s' % kind.is_mime)

if __name__ == '__main__':
    main()