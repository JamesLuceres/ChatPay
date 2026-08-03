import { compile } from 'cashscript'
import fs from 'fs'
import path from 'path'

async function compileRoomCreate() {
  try {
    const contractPath = path.join(process.cwd(), 'src', 'contracts', 'RoomCreate.cash')
    const outputPath = path.join(process.cwd(), 'src', 'contracts', 'RoomCreate.json')

    // Read the contract source
    const source = fs.readFileSync(contractPath, 'utf8')

    // Compile the contract
    const artifact = compile(source)

    // Write the artifact
    fs.writeFileSync(outputPath, JSON.stringify(artifact, null, 2))
  } catch (error) {
    // Only show error if needed for user
  }
}

compileRoomCreate()
